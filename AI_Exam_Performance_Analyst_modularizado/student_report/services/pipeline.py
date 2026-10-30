"""Flujo principal: datos -> perfil -> (LLM -> validación) -> HTML.

Reproduce paso a paso la versión v9 del script original, con los
mismos mensajes de consola (se pueden silenciar o redirigir con
``echo``) y el mismo orden de operaciones.

Cambios v9 integrados:

- ``--analisis-ia false``: no se llama al LLM ni se valida ningún JSON;
  el informe HTML se genera solo con los resultados académicos.
- La respuesta JSON del LLM se conserva ÚNICAMENTE en memoria: no se
  crea ninguna carpeta ni fichero ``.json`` en disco.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from student_report.config.settings import (
    BASE_CSS_PATH,
    DEFAULT_LANGUAGE,
    EXTRA_INFO_CSV_PATH,
    LLM_MODEL,
    OUTPUT_DIR,
    RESULTS_CSV_PATH,
)
from student_report.core.analysis import (
    build_analysis_frame,
    build_student_profile,
    get_evaluation_keys,
)
from student_report.core.data_loader import (
    ensure_not_empty,
    filter_student_results,
    load_results,
    normalize_results,
    parse_evaluation_date,
)
from student_report.core.exceptions import LLMReportError
from student_report.core.extra_info import (
    build_report_context,
    load_extra_info,
    merge_extra_info,
)
from student_report.core.validation import (
    validate_pedagogical_coherence,
    validate_report_structure,
)
from student_report.llm.client import OpenRouterClient, get_api_key, parse_json_response
from student_report.llm.prompt_builder import build_prompt
from student_report.reports.html_renderer import write_html_report

__all__ = ["LLMClient", "PipelineConfig", "PipelineResult", "run_pipeline"]

Echo = Callable[..., None]


class LLMClient(Protocol):
    """Cualquier objeto con ``complete(prompt) -> str`` sirve como cliente."""

    def complete(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class PipelineConfig:
    """Parámetros de una ejecución del flujo.

    Los valores por defecto coinciden con los literales de la versión
    v9 del script original.
    """

    student_id: int
    evaluation_date: str
    language: str = DEFAULT_LANGUAGE
    ai_analysis: bool = True
    results_csv: str | Path = RESULTS_CSV_PATH
    extra_info_csv: str | Path = EXTRA_INFO_CSV_PATH
    output_dir: str | Path = OUTPUT_DIR
    base_css: str | Path = BASE_CSS_PATH
    model: str = LLM_MODEL


@dataclass
class PipelineResult:
    """Artefactos producidos por :func:`run_pipeline`.

    ``report`` es el JSON del LLM validado, conservado en memoria
    (nunca en disco). Con ``ai_analysis=False`` contiene únicamente
    ``{"student_data": <perfil>}``.
    """

    student_profile: dict[str, Any]
    report: dict[str, Any]
    html_path: Path
    warnings: list[str] = field(default_factory=list)
    analysis: pd.DataFrame | None = None


def _print_warnings(warnings: list[str], echo: Echo) -> None:
    """Muestra los avisos de coherencia o el mensaje de validación superada."""
    if warnings:
        echo("\nAVISOS DE COHERÈNCIA PEDAGÒGICA:")
        for warning in warnings:
            echo(f"- {warning}")
    else:
        echo(
            "Validació pedagògica superada: "
            "no s'han detectat incoherències bàsiques."
        )


def _request_report(
    prompt: str,
    config: PipelineConfig,
    llm_client: LLMClient | None,
    echo: Echo,
) -> dict[str, Any]:
    """Obtiene el informe JSON del LLM y lo devuelve (solo en memoria).

    Raises:
        RuntimeError: falta ``OPENROUTER_API_KEY`` (si no se inyecta cliente).
        LLMReportError: respuesta vacía, JSON inválido u otro error de la API.
    """
    if llm_client is None:
        api_key = get_api_key()
        echo(f"Clau API recuperada: {'Sí' if api_key else 'No'}")
        if not api_key:
            raise RuntimeError("Falta la variable d'entorn OPENROUTER_API_KEY.")
        llm_client = OpenRouterClient(api_key=api_key, model=config.model)

    response: str | None = None
    try:
        response = llm_client.complete(prompt)
        report = parse_json_response(response)

        # El JSON es conserva únicament en memòria per a la validació
        # i la generació de l'HTML. No es crea cap fitxer ni carpeta JSON.
        echo("Informe JSON generat en memòria (sense desar cap fitxer).")
        return report

    except json.JSONDecodeError as exc:
        echo("Error: el model no ha retornat un JSON vàlid.")
        echo("Resposta rebuda:")
        echo(response)
        raise LLMReportError("El model no ha retornat un JSON vàlid.") from exc

    except Exception as exc:  # noqa: BLE001 - se re-lanza tipado
        echo(f"Error en generar l'informe amb IA: {exc}")
        raise LLMReportError(str(exc)) from exc


def run_pipeline(
    config: PipelineConfig,
    llm_client: LLMClient | None = None,
    echo: Echo | None = print,
) -> PipelineResult:
    """Ejecuta el flujo completo para un alumno y una fecha.

    Args:
        config: parámetros de la ejecución.
        llm_client: cliente LLM alternativo (útil en tests). Si es
            ``None`` se usa OpenRouter con ``OPENROUTER_API_KEY``.
        echo: función de salida por consola; ``None`` silencia la salida.

    Returns:
        :class:`PipelineResult` con perfil, informe, avisos y ruta HTML.

    Raises:
        FileNotFoundError: faltan CSV o ``style.css``.
        NoRecordsFoundError: no hay notas del alumno en la fecha.
        LLMReportError: el LLM no devuelve un JSON utilizable.
        ReportValidationError: el JSON no supera la validación.
        ExtraInfoError: datos complementarios inválidos o ausentes.
    """
    out: Echo = echo if echo is not None else (lambda *a, **k: None)

    # 1-4. Carga, normalización y filtrado
    df = normalize_results(load_results(config.results_csv))
    evaluation_date = parse_evaluation_date(config.evaluation_date)
    student_id_str = str(config.student_id).strip()

    df = filter_student_results(df, student_id_str, evaluation_date)
    out(f"Files trobades: {len(df)}")
    ensure_not_empty(df, student_id_str, evaluation_date)

    # 5-12. Análisis
    keys = get_evaluation_keys(df)
    analysis = build_analysis_frame(df, config.student_id, evaluation_date, keys)

    out("\nResultats de l'alumne:")
    out(df)
    out("\nPerfil de l'alumne:")
    out(analysis)

    # 14. Perfil para el LLM
    profile = build_student_profile(analysis)
    out("\nPerfil preparat per al LLM:")
    out(profile)

    # 15-18. Prompt
    prompt = build_prompt(profile, config.language)
    out("\\nPROMPT PREPARAT PER AL LLM:\\n")  # literal, como en el original
    out(prompt)

    # 19-21. LLM y validación (solo con --analisis-ia true)
    report: dict[str, Any]
    warnings: list[str] = []

    if config.ai_analysis:
        report = _request_report(prompt, config, llm_client, out)

        validate_report_structure(report)
        out("Estructura bàsica del JSON validada correctament.")
        warnings = validate_pedagogical_coherence(report, profile)
        _print_warnings(warnings, out)
    else:
        out(
            "Anàlisi amb IA desactivada: no es farà cap crida al LLM "
            "ni es generarà JSON pedagògic."
        )
        # El informe se limita a los datos académicos reales del alumno.
        report = {"student_data": profile}

    # 23. Datos complementarios
    df_extra = load_extra_info(config.extra_info_csv)
    df_final, rows_without_info = merge_extra_info(analysis, df_extra)
    if rows_without_info:
        out(
            "Avís: no s'ha trobat informació complementària "
            f"per a {rows_without_info} registre(s)."
        )
    out("Dades complementàries preparades.")
    out(f"Files a l'informe: {len(df_final)}")

    # 24. Informe HTML
    extra_info = build_report_context(df_final, student_id_str, keys.evaluation_id)
    html_path = write_html_report(
        report=report,
        language=config.language,
        extra_info=extra_info,
        output_dir=config.output_dir,
        base_css_path=config.base_css,
        include_ai_analysis=config.ai_analysis,
    )
    out(f"Informe HTML generat: {html_path}")

    return PipelineResult(
        student_profile=profile,
        report=report,
        html_path=html_path,
        warnings=warnings,
        analysis=analysis,
    )
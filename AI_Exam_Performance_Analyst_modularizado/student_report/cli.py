"""Interfaz de línea de comandos.

Argumentos (versión v9):

- ``--idalumne``: identificador del alumno (obligatorio).
- ``--data``: fecha de la evaluación ``YYYY-MM-DD`` (obligatorio).
- ``--language``: código ISO 639-1 ``ca`` | ``es`` | ``en``
  (se aceptan también los nombres internos ``catala``, ``castellano``
  y ``english`` por compatibilidad).
- ``--analisis-ia``: ``true`` | ``false``. Por defecto ``true``: activa
  el análisis pedagógico mediante el LLM. Con ``false`` no se llama al
  LLM y el informe se genera solo con los resultados académicos.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from student_report.config.settings import (
    DEFAULT_LANGUAGE_CODE,
    INTERNAL_LANGUAGE_CODES,
    LANGUAGE_CODES,
    SUPPORTED_LANGUAGES,
    normalize_language,
)
from student_report.core.exceptions import NoRecordsFoundError
from student_report.services.pipeline import (
    PipelineConfig,
    PipelineResult,
    run_pipeline,
)

__all__ = ["build_parser", "parse_bool", "parse_args", "main"]


def parse_bool(value: str) -> bool:
    """Convierte el valor de ``--analisis-ia`` en ``bool``.

    Solo acepta ``true`` y ``false`` (insensible a mayúsculas).

    Raises:
        argparse.ArgumentTypeError: con cualquier otro valor.
    """
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("El valor ha de ser true o false.")


def build_parser() -> argparse.ArgumentParser:
    """Crea el parser con los argumentos de la versión v9."""
    parser = argparse.ArgumentParser(
        description="Analitza els resultats d'un alumne."
    )
    parser.add_argument("--idalumne", type=int, required=True,
                        help="ID de l'alumne")
    parser.add_argument("--data", required=True,
                        help="Data de l'avaluació en format YYYY-MM-DD")
    parser.add_argument(
        "--language",
        type=str,
        choices=[*LANGUAGE_CODES, *SUPPORTED_LANGUAGES],
        default=DEFAULT_LANGUAGE_CODE,
        help=(
            "Idioma de l'informe segons ISO 639-1: "
            "ca (català), es (castellà), en (anglès)"
        ),
    )
    parser.add_argument(
        "--analisis-ia",
        type=parse_bool,
        default=True,
        metavar="{true,false}",
        help=(
            "Activa o desactiva l'anàlisi amb IA "
            "(per defecte: true)"
        ),
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> PipelineConfig:
    """Convierte los argumentos de consola en un :class:`PipelineConfig`.

    La conversión del código ISO 639-1 al idioma interno se hace con la
    función centralizada :func:`student_report.config.settings.normalize_language`.
    """
    args = build_parser().parse_args(argv)
    return PipelineConfig(
        student_id=args.idalumne,
        evaluation_date=args.data,
        language=normalize_language(args.language),
        ai_analysis=args.analisis_ia,
    )


def main(argv: Sequence[str] | None = None) -> PipelineResult:
    """Punto de entrada de consola.

    Si no hay registros termina con ``SystemExit`` y el mismo mensaje
    que el script original.
    """
    config = parse_args(argv)
    try:
        return run_pipeline(config)
    except NoRecordsFoundError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
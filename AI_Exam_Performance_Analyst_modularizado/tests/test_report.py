"""Pruebas de integración de la versión v9 en el paquete modularizado.

NO se realizan llamadas reales al LLM: se usa un cliente simulado
(``MockLLM``) que construye una respuesta JSON válida a partir del
perfil incluido en el prompt.

Ejecución::

    python -m pytest tests -q
"""

from __future__ import annotations

import json
import math
import re
import shutil
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from student_report.cli import parse_args, parse_bool  # noqa: E402
from student_report.config import settings  # noqa: E402
from student_report.config.settings import normalize_language  # noqa: E402
from student_report.reports.html_renderer import (  # noqa: E402
    exam_state,
    render_report_html,
)
from student_report.services.pipeline import (  # noqa: E402
    PipelineConfig,
    run_pipeline,
)

DATE = "2026-06-20"


# ------------------------------------------------------------------
# Cliente LLM simulado (no se hace ninguna llamada real)
# ------------------------------------------------------------------

class MockLLM:
    """Cliente LLM falso: responde un JSON válido derivado del perfil."""

    def __init__(self) -> None:
        self.calls = 0
        self.last_prompt = ""

    def complete(self, prompt: str) -> str:
        self.calls += 1
        self.last_prompt = prompt
        block = prompt.split("PERFIL INDIVIDUAL DE ALUMNO:")[1]
        block = block.split("ESQUEMA JSON OBLIGATORIO:")[0]
        profile = json.loads(block.strip())
        skills = profile["skills"]
        best = profile["best_skill"]
        worst = profile["weakest_skill"]
        return json.dumps(
            {
                "student_data": profile,
                "strengths": [
                    {
                        "skill": best,
                        "score": skills[best],
                        "observation": "Molt bé, continua així!",
                    }
                ],
                "areas_to_improve": [
                    {
                        "skill": worst,
                        "score": skills[worst],
                        "priority": "High",
                        "observation": "Cal practicar més aquesta part.",
                    }
                ],
                "skills_balance": "Les cinc competències contribueixen un 20%.",
                "proposed_activities": [
                    {
                        "skill": worst,
                        "description": "Activitat 1",
                        "procedure": "Pas 1",
                        "learning_objective": "Objectiu 1",
                    },
                    {
                        "skill": worst,
                        "description": "Activitat 2",
                        "procedure": "Pas 2",
                        "learning_objective": "Objectiu 2",
                    },
                ],
            },
            ensure_ascii=False,
        )


# ------------------------------------------------------------------
# Utilidades de prueba
# ------------------------------------------------------------------

def make_config(
    tmp_path: Path, student_id: int, language: str = "ca",
    ai_analysis: bool = True,
) -> PipelineConfig:
    return PipelineConfig(
        student_id=student_id,
        evaluation_date=DATE,
        language=normalize_language(language),
        ai_analysis=ai_analysis,
        results_csv=PROJECT_ROOT / "data" / "NOTA_PARCIAL_PONDERADA_ALUMN.csv",
        extra_info_csv=PROJECT_ROOT / "data"
        / "INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv",
        output_dir=tmp_path / "reports",
        base_css=PROJECT_ROOT / "style.css",
    )


@pytest.fixture()
def tmp_reports(tmp_path: Path) -> Path:
    """Directorio temporal para los informes generados."""
    folder = tmp_path / "reports"
    folder.mkdir()
    return folder


# ------------------------------------------------------------------
# 1. Argumentos CLI
# ------------------------------------------------------------------

def test_cli_accepts_iso_language_and_analisis_ia() -> None:
    config = parse_args(
        ["--idalumne", "1701", "--data", DATE,
         "--language", "es", "--analisis-ia", "false"]
    )
    assert config.student_id == 1701
    assert config.evaluation_date == DATE
    assert config.language == "castellano"
    assert config.ai_analysis is False


def test_cli_analisis_ia_defaults_to_true() -> None:
    config = parse_args(["--idalumne", "1701", "--data", DATE, "--language", "ca"])
    assert config.ai_analysis is True


def test_cli_analisis_ia_rejects_other_values() -> None:
    with pytest.raises(argparse_error()):
        parse_bool("maybe")


def argparse_error() -> type[Exception]:
    import argparse

    return argparse.ArgumentTypeError


def test_language_conversion_is_centralized() -> None:
    assert settings.normalize_language("ca") == "catala"
    assert settings.normalize_language("es") == "castellano"
    assert settings.normalize_language("en") == "english"
    # Los tres idiomas internos siguen funcionando (compatibilidad).
    for code, internal in settings.LANGUAGE_CODES.items():
        assert settings.INTERNAL_LANGUAGE_CODES[internal] == code


# ------------------------------------------------------------------
# 2. Config externa: Pass_mark (desde .env)
# ------------------------------------------------------------------

def test_pass_mark_comes_from_env_config() -> None:
    assert isinstance(settings.Pass_mark, (int, float))
    assert settings.Pass_mark == settings.DEFAULT_PASS_MARK


# ------------------------------------------------------------------
# 3. Clasificación Pass / No pass
# ------------------------------------------------------------------

@pytest.mark.parametrize(
    ("average", "pass_mark", "expected"),
    [
        (50.0, 50.0, "pass"),        # exactamente igual -> aprobado
        (78.8, 50.0, "pass"),        # superior -> aprobado
        (44.75, 50.0, "no-pass"),    # inferior -> suspenso
        (None, 50.0, "unavailable"),
        (float("nan"), 50.0, "unavailable"),
        (78.8, None, "unavailable"),
        ("", 50.0, "unavailable"),
    ],
)
def test_exam_state(average, pass_mark, expected) -> None:
    assert exam_state(average, pass_mark) == expected


# ------------------------------------------------------------------
# 4. Ejecución del flujo con LLM simulado
# ------------------------------------------------------------------

def test_ai_disabled_skips_llm_and_generates_html(tmp_path: Path) -> None:
    mock = MockLLM()
    result = run_pipeline(make_config(tmp_path, 1701, "ca", ai_analysis=False),
                          llm_client=mock, echo=lambda *a, **k: None)

    assert mock.calls == 0  # no se llama al LLM
    assert set(result.report.keys()) == {"student_data"}
    html = result.html_path.read_text(encoding="utf-8")
    # El informe se genera igualmente, pero sin la sección de IA.
    assert 'lang="ca"' in html
    assert "Pass/No pass" in html
    assert "Anàlisi pedagògica assistida per IA" not in html
    assert "Resultat final" in html
    assert not list(tmp_path.rglob("*.json"))  # sin ficheros JSON


def test_ai_enabled_uses_mock_and_validates_json(tmp_path: Path) -> None:
    mock = MockLLM()
    result = run_pipeline(make_config(tmp_path, 1701, "es", ai_analysis=True),
                          llm_client=mock, echo=lambda *a, **k: None)

    assert mock.calls == 1
    assert set(result.report.keys()) == {
        "student_data", "strengths", "areas_to_improve",
        "skills_balance", "proposed_activities",
    }
    html = result.html_path.read_text(encoding="utf-8")
    assert "Molt bé, continua així!" in html
    assert "Análisis pedagógico asistido por IA" in html
    assert not list(tmp_path.rglob("*.json"))  # JSON solo en memoria


@pytest.mark.parametrize(
    ("code", "result_final", "pass_label"),
    [
        ("ca", "Resultat final", "Llindar de superació"),
        ("es", "Resultado final", "Nota de aprobado"),
        ("en", "Final result", "Pass mark"),
    ],
)
def test_three_languages(tmp_path: Path, code, result_final, pass_label) -> None:
    result = run_pipeline(
        make_config(tmp_path, 1701, code, ai_analysis=False),
        llm_client=MockLLM(), echo=lambda *a, **k: None,
    )
    html = result.html_path.read_text(encoding="utf-8")
    assert f'lang="{code}"' in html
    assert result_final in html
    assert pass_label in html
    # El nombre del fichero usa el código ISO 639-1.
    assert result.html_path.name.endswith(f"_{code}.html")
    # Pie en dos bandas con los datos reales de contacto.
    assert '<span class="footer-school-name">Escola Comunica&#x27;t</span>' in html
    for fragment in (
        "tel:+34934262479",
        "https://wa.me/34601302029",
        "mailto:info@comunicat.school",
        "https://www.comunicat.school",
        "Entença, 89, 08015, Barcelona",
    ):
        assert fragment in html


# ------------------------------------------------------------------
# 5. Pass/No pass en el HTML
# ------------------------------------------------------------------

def test_pass_status_equal_to_threshold_is_pass(tmp_path: Path) -> None:
    # El alumno 1702 tiene de media exactamente Pass_mark (50).
    result = run_pipeline(
        make_config(tmp_path, 1702, "en", ai_analysis=False),
        llm_client=MockLLM(), echo=lambda *a, **k: None,
    )
    html = result.html_path.read_text(encoding="utf-8")
    assert 'exam-status-pass' in html
    assert 'exam-status-no-pass' not in html


def test_pass_status_below_threshold_is_no_pass(tmp_path: Path) -> None:
    # El alumno 1701 tiene de media 44.75 (< Pass_mark).
    result = run_pipeline(
        make_config(tmp_path, 1701, "en", ai_analysis=False),
        llm_client=MockLLM(), echo=lambda *a, **k: None,
    )
    html = result.html_path.read_text(encoding="utf-8")
    assert 'exam-status-no-pass' in html
    assert 'exam-status-unavailable' not in html


def test_missing_average_is_unavailable(tmp_path: Path) -> None:
    report = {
        "student_data": {
            "student_id": 1701,
            "evaluation_date": DATE,
            "skills": {"grammar": 80.0, "listening": 80.0, "reading": 80.0,
                       "speaking": 80.0, "writing": 80.0},
            "average": None,
            "best_skill": "grammar",
            "weakest_skill": "writing",
            "range": 0.0,
        }
    }
    html = render_report_html(report, "catala", include_ai_analysis=False)
    assert 'exam-status-unavailable' in html
    assert "Resultat no disponible" in html


def test_pass_bar_uses_config_threshold(tmp_path: Path) -> None:
    result = run_pipeline(
        make_config(tmp_path, 1701, "ca", ai_analysis=False),
        llm_client=MockLLM(), echo=lambda *a, **k: None,
    )
    html = result.html_path.read_text(encoding="utf-8")
    # El marcador del umbral se posiciona en Pass_mark / 100 (50 %).
    threshold = float(settings.Pass_mark)
    expected = f"--marker-position: {threshold:.4f}%"
    assert expected in html
    # El marcador del alumno usa la MISMA escala (0-100).
    assert "pass-threshold-marker" in html
    assert "pass-score-marker" in html
    assert "pass-bar-horizontal" in html


def test_no_yellow_border_around_pass_column() -> None:
    css = (PROJECT_ROOT / "student_report" / "reports" / "assets"
           / "report.css").read_text(encoding="utf-8")
    rule = re.search(r"\.pass-status-cell\s*\{[^}]*\}", css)
    assert rule is not None
    assert "border" not in rule.group(0)  # sin contorno amarillo


# ------------------------------------------------------------------
# 6. Filas dinámicas de fortalezas y mejoras
# ------------------------------------------------------------------

def test_strengths_and_improvements_single_dynamic_row() -> None:
    report = {
        "student_data": {
            "student_id": 1701,
            "evaluation_date": DATE,
            "skills": {"grammar": 90.0, "listening": 70.0, "reading": 85.0,
                       "speaking": 60.0, "writing": 65.0},
            "average": 74.0,
            "best_skill": "grammar",
            "weakest_skill": "speaking",
            "range": 30.0,
        },
        "strengths": [
            {"skill": "grammar", "score": 90.0, "observation": "obs 1"},
            {"skill": "reading", "score": 85.0, "observation": "obs 2"},
            {"skill": "listening", "score": 70.0, "observation": "obs 3"},
        ],
        "areas_to_improve": [
            {"skill": "speaking", "score": 60.0, "priority": "High",
             "observation": "obs A"},
            {"skill": "writing", "score": 65.0, "priority": "Medium",
             "observation": "obs B"},
        ],
        "skills_balance": "text",
        "proposed_activities": [
            {"skill": "speaking", "description": "d", "procedure": "p",
             "learning_objective": "o"},
            {"skill": "writing", "description": "d", "procedure": "p",
             "learning_objective": "o"},
        ],
    }
    html = render_report_html(report, "castellano")
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in html
    assert "repeat(2, minmax(0, 1fr))" in html
    assert html.count('class="pedagogy-card strength-card"') == 3
    assert html.count('class="pedagogy-card improvement-card"') == 2


def test_empty_ai_sections_show_localized_empty_state() -> None:
    report = {
        "student_data": {
            "student_id": 1, "evaluation_date": DATE,
            "skills": {"grammar": 50.0, "listening": 50.0, "reading": 50.0,
                       "speaking": 50.0, "writing": 50.0},
            "average": 50.0, "best_skill": "grammar",
            "weakest_skill": "grammar", "range": 0.0,
        },
        "strengths": [], "areas_to_improve": [],
        "skills_balance": "", "proposed_activities": [],
    }
    html = render_report_html(report, "english")
    assert "No strengths have been recorded." in html
    assert "No areas for improvement have been recorded." in html


# ------------------------------------------------------------------
# 7. Bloque de marca y pie
# ------------------------------------------------------------------

def test_brand_block_in_header(tmp_path: Path) -> None:
    result = run_pipeline(
        make_config(tmp_path, 1701, "ca", ai_analysis=False),
        llm_client=MockLLM(), echo=lambda *a, **k: None,
    )
    html = result.html_path.read_text(encoding="utf-8")
    assert '<span class="brand-text">Comunica-T</span>' in html
    assert '<span class="brand-subtext">School</span>' in html
    assert 'class="school-logo"' in html
    assert settings.SCHOOL_LOGO_URL in html
    # Fotografía del alumno con borde amarillo compartido.
    assert "--highlight-yellow: #f4d800" in (
        (PROJECT_ROOT / "style.css").read_text(encoding="utf-8")
    )
    css = ((PROJECT_ROOT / "student_report" / "reports" / "assets"
            / "report.css").read_text(encoding="utf-8"))
    assert "border: 3px solid var(--highlight-yellow);" in css
    assert "border: 2px solid var(--highlight-yellow);" in css
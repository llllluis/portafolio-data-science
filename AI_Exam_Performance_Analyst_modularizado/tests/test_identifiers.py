"""Pruebas de la identificación por ``IDALUMNE + IDEVALUACIO + IDCURS``.

Cubren las siete pruebas pedidas: combinación válida, dos cursos con la
misma fecha, dos evaluaciones del mismo curso, combinación inexistente,
duplicados, IA activada/desactivada y rutas de CSV configurables.

No se realizan llamadas reales al LLM.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from student_report.cli import parse_args  # noqa: E402
from student_report.config import settings  # noqa: E402
from student_report.core.exceptions import (  # noqa: E402
    DataValidationError,
    ExtraInfoError,
    MultipleRecordsFoundError,
    NoRecordsFoundError,
)
from student_report.services.pipeline import (  # noqa: E402
    PipelineConfig,
    run_pipeline,
)

SKILLS = ("GRAMMAR", "LISTENING", "READING", "SPEAKING", "WRITING")

# (IDALUMNE, DATA, IDEVALUACIO, IDCURS, notas de las 5 habilidades)
RESULTS_ROWS = [
    (1701, "20/06/2026", 101, 7, (45, 38.5, 52, 41, 47.25)),
    (1701, "20/06/2026", 101, 8, (70, 71, 72, 73, 74)),
    (1701, "15/09/2026", 102, 7, (60, 61, 62, 63, 64)),
]


class MockLLM:
    """Cliente LLM falso: JSON válido derivado del perfil del prompt."""

    def __init__(self) -> None:
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        block = prompt.split("PERFIL INDIVIDUAL DE ALUMNO:")[1]
        block = block.split("ESQUEMA JSON OBLIGATORIO:")[0]
        profile = json.loads(block.strip())
        best, worst = profile["best_skill"], profile["weakest_skill"]
        return json.dumps({
            "student_data": profile,
            "strengths": [{"skill": best,
                           "score": profile["skills"][best],
                           "observation": "ok"}],
            "areas_to_improve": [{"skill": worst,
                                  "score": profile["skills"][worst],
                                  "priority": "High",
                                  "observation": "cal practicar"}],
            "skills_balance": "Les cinc competències pesen un 20%.",
            "proposed_activities": [
                {"skill": worst, "description": "A", "procedure": "P",
                 "learning_objective": "O"},
                {"skill": worst, "description": "B", "procedure": "P",
                 "learning_objective": "O"},
            ],
        }, ensure_ascii=False)


def _num(value: float) -> str:
    return str(value).replace(".", ",")


def write_results(path: Path, rows=RESULTS_ROWS) -> Path:
    lines = ["IDALUMNE;DATA;IDEVALUACIO;IDCURS;MATERIA;PERCENTATGE"]
    for student, date, evaluation, course, scores in rows:
        for skill, score in zip(SKILLS, scores):
            lines.append(
                f"{student};{date};{evaluation};{course};{skill};{_num(score)}"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_extra(path: Path, rows=RESULTS_ROWS) -> Path:
    lines = [
        "IDALUMNE;IDEVALUACIO;IDCURS;COMENTARI;PROFE;NOMCURS;"
        "NOM_ALUMNE;DESCRIPCIO;EJERCICIO_ESCOLAR"
    ]
    for student, _date, evaluation, course, _scores in rows:
        lines.append(
            f"{student};{evaluation};{course};Comentari {course};"
            f"Anna Grace;Curs {course};Alumne {course};"
            "Avaluació final;2025-2026"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture()
def dataset(tmp_path: Path) -> dict[str, Path]:
    return {
        "results": write_results(tmp_path / "results.csv"),
        "extra": write_extra(tmp_path / "extra.csv"),
    }


def make_config(
    tmp_path: Path,
    data: dict[str, Path],
    student_id: int = 1701,
    evaluation_id: int = 101,
    course_id: int | str = 7,
    ai_analysis: bool = False,
) -> PipelineConfig:
    return PipelineConfig(
        student_id=student_id,
        evaluation_id=evaluation_id,
        course_id=course_id,
        language="catala",
        ai_analysis=ai_analysis,
        results_csv=data["results"],
        extra_info_csv=data["extra"],
        output_dir=tmp_path / "reports",
        base_css=PROJECT_ROOT / "style.css",
    )


def run(config: PipelineConfig, mock: MockLLM | None = None):
    return run_pipeline(
        config, llm_client=mock or MockLLM(), echo=lambda *a, **k: None
    )


# ------------------------------------------------------------------
# Prueba 1: combinación válida y fecha leída del CSV
# ------------------------------------------------------------------

def test_valid_combination_reads_date_from_csv(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    result = run(make_config(tmp_path, dataset))
    profile = result.student_profile

    assert profile["student_id"] == 1701
    assert profile["evaluation_date"] == "2026-06-20"  # desde DATA del CSV
    assert profile["skills"]["grammar"] == 45.0
    assert profile["average"] == 44.75


# ------------------------------------------------------------------
# Prueba 2: mismo alumno y fecha, distinto curso
# ------------------------------------------------------------------

def test_same_student_and_date_different_course(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    first = run(make_config(tmp_path, dataset, course_id=7))
    second = run(make_config(tmp_path, dataset, course_id=8))

    assert first.student_profile["skills"]["grammar"] == 45.0
    assert second.student_profile["skills"]["grammar"] == 70.0
    # Misma fecha en ambos, pero ficheros distintos: no se sobrescriben.
    assert first.student_profile["evaluation_date"] == "2026-06-20"
    assert second.student_profile["evaluation_date"] == "2026-06-20"
    assert first.html_path != second.html_path
    assert first.html_path.is_file() and second.html_path.is_file()
    assert "_101_7_ca.html" in first.html_path.name
    assert "_101_8_ca.html" in second.html_path.name


# ------------------------------------------------------------------
# Prueba 3: mismo alumno y curso, distinta evaluación
# ------------------------------------------------------------------

def test_same_student_and_course_different_evaluation(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    june = run(make_config(tmp_path, dataset, evaluation_id=101))
    september = run(make_config(tmp_path, dataset, evaluation_id=102))

    assert june.student_profile["skills"]["grammar"] == 45.0
    assert june.student_profile["evaluation_date"] == "2026-06-20"
    assert september.student_profile["skills"]["grammar"] == 60.0
    assert september.student_profile["evaluation_date"] == "2026-09-15"
    assert june.html_path != september.html_path


# ------------------------------------------------------------------
# Prueba 4: combinación inexistente
# ------------------------------------------------------------------

def test_unknown_combination_raises_with_ids(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    with pytest.raises(NoRecordsFoundError) as excinfo:
        run(make_config(tmp_path, dataset, evaluation_id=999))
    message = str(excinfo.value)
    assert "IDALUMNE=1701" in message
    assert "IDEVALUACIO=999" in message
    assert "IDCURS=7" in message


def test_unknown_course_raises(tmp_path: Path, dataset: dict[str, Path]) -> None:
    with pytest.raises(NoRecordsFoundError):
        run(make_config(tmp_path, dataset, course_id=99))


# ------------------------------------------------------------------
# Prueba 5: combinación duplicada
# ------------------------------------------------------------------

def test_duplicated_skill_raises_controlled_error(tmp_path: Path) -> None:
    rows = list(RESULTS_ROWS) + [
        (1701, "20/06/2026", 101, 7, (99, 0, 0, 0, 0))
    ]
    data = {
        "results": write_results(tmp_path / "dup.csv", rows),
        "extra": write_extra(tmp_path / "extra.csv"),
    }
    with pytest.raises(MultipleRecordsFoundError) as excinfo:
        run(make_config(tmp_path, data))
    message = str(excinfo.value)
    assert "GRAMMAR" in message
    assert "IDALUMNE=1701" in message


def test_duplicated_extra_info_raises(tmp_path: Path, dataset: dict[str, Path]) -> None:
    duplicated = write_extra(
        tmp_path / "extra_dup.csv",
        list(RESULTS_ROWS) + [(1701, "20/06/2026", 101, 7, (1, 2, 3, 4, 5))],
    )
    config = make_config(tmp_path, dataset)
    config = PipelineConfig(**{**config.__dict__, "extra_info_csv": duplicated})
    with pytest.raises(ExtraInfoError):
        run(config)


# ------------------------------------------------------------------
# Prueba 6: IA desactivada y activada
# ------------------------------------------------------------------

def test_ai_disabled_does_not_call_llm(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    mock = MockLLM()
    result = run(make_config(tmp_path, dataset, ai_analysis=False), mock)
    assert mock.calls == 0
    assert set(result.report) == {"student_data"}
    assert "Anàlisi pedagògica assistida per IA" not in result.html_content


def test_ai_enabled_calls_llm_and_validates(
    tmp_path: Path, dataset: dict[str, Path]
) -> None:
    mock = MockLLM()
    result = run(make_config(tmp_path, dataset, ai_analysis=True), mock)
    assert mock.calls == 1
    assert set(result.report) == {
        "student_data", "strengths", "areas_to_improve",
        "skills_balance", "proposed_activities",
    }
    # La fecha que recibe la IA es la del CSV.
    assert result.report["student_data"]["evaluation_date"] == "2026-06-20"
    assert not list(tmp_path.rglob("*.json"))


# ------------------------------------------------------------------
# Prueba 7: rutas de CSV configurables mediante .env
# ------------------------------------------------------------------

def test_csv_paths_are_read_from_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    alt = tmp_path / "alt"
    alt.mkdir(parents=True, exist_ok=True)
    results = write_results(alt / "r.csv")
    extra = write_extra(alt / "e.csv")
    monkeypatch.setenv("RESULTS_CSV_PATH", str(results))
    monkeypatch.setenv("EXTRA_INFO_CSV_PATH", str(extra))
    try:
        reloaded = importlib.reload(settings)
        assert reloaded.RESULTS_CSV_PATH == results.resolve()
        assert reloaded.EXTRA_INFO_CSV_PATH == extra.resolve()
    finally:
        monkeypatch.delenv("RESULTS_CSV_PATH", raising=False)
        monkeypatch.delenv("EXTRA_INFO_CSV_PATH", raising=False)
        importlib.reload(settings)


def test_relative_env_path_is_resolved_against_project_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RESULTS_CSV_PATH", "data/NOTA_PARCIAL_PONDERADA_ALUMN.csv")
    try:
        reloaded = importlib.reload(settings)
        expected = (PROJECT_ROOT / "data/NOTA_PARCIAL_PONDERADA_ALUMN.csv").resolve()
        assert reloaded.RESULTS_CSV_PATH == expected
        assert reloaded.RESULTS_CSV_PATH.is_file()
    finally:
        monkeypatch.delenv("RESULTS_CSV_PATH", raising=False)
        importlib.reload(settings)


def test_missing_csv_reports_env_variable(tmp_path: Path) -> None:
    data = {"results": tmp_path / "no-existe.csv",
            "extra": tmp_path / "tampoco.csv"}
    with pytest.raises(FileNotFoundError) as excinfo:
        run(make_config(tmp_path, data))
    assert "RESULTS_CSV_PATH" in str(excinfo.value)


# ------------------------------------------------------------------
# Validaciones adicionales de datos
# ------------------------------------------------------------------

def test_missing_column_raises(tmp_path: Path, dataset: dict[str, Path]) -> None:
    broken = tmp_path / "sin_idcurs.csv"
    broken.write_text(
        "IDALUMNE;DATA;IDEVALUACIO;MATERIA;PERCENTATGE\n"
        "1701;20/06/2026;101;GRAMMAR;45\n",
        encoding="utf-8",
    )
    config = make_config(tmp_path, {**dataset, "results": broken})
    with pytest.raises(DataValidationError) as excinfo:
        run(config)
    assert "IDCURS" in str(excinfo.value)


def test_invalid_date_raises(tmp_path: Path) -> None:
    rows = [
        (1701, "no-es-una-fecha", 101, 7, (45, 38.5, 52, 41, 47.25)),
    ]
    data = {
        "results": write_results(tmp_path / "bad_date.csv", rows),
        "extra": write_extra(tmp_path / "extra.csv"),
    }
    with pytest.raises(DataValidationError) as excinfo:
        run(make_config(tmp_path, data))
    assert "DATA" in str(excinfo.value)


def test_cli_no_longer_accepts_data_flag() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--idalumne", "1701", "--idevaluacio", "101",
                    "--idcurs", "7", "--data", "2026-06-20"])


def test_default_language_is_english_when_omitted() -> None:
    """Sin --language, el informe se genera en inglés."""
    config = parse_args(["--idalumne", "1701", "--idevaluacio", "101",
                         "--idcurs", "8"])
    assert config.language == "english"
    assert settings.DEFAULT_LANGUAGE == "english"
    assert settings.DEFAULT_LANGUAGE_CODE == "en"


def test_pipeline_config_defaults_to_english() -> None:
    config = PipelineConfig(student_id=1701, evaluation_id=101, course_id=8)
    assert config.language == "english"


def test_cli_course_id_accepts_text_and_numbers() -> None:
    numeric = parse_args(["--idalumne", "1701", "--idevaluacio", "101",
                          "--idcurs", "7"])
    textual = parse_args(["--idalumne", "1701", "--idevaluacio", "101",
                          "--idcurs", "A2-GEN"])
    assert numeric.course_id == 7
    assert textual.course_id == "A2-GEN"

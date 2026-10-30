"""Pruebas de la configuración del modelo LLM vía ``.env`` (MODEL_LLM).

NO se realizan llamadas reales al LLM.

Ejecución::

    python -m pytest tests/test_model_config.py -q
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _reload_settings(monkeypatch, env_value: str | None):
    """Recarga ``settings`` con ``MODEL_LLM`` fijado o eliminado."""
    if env_value is None:
        monkeypatch.delenv("MODEL_LLM", raising=False)
    else:
        monkeypatch.setenv("MODEL_LLM", env_value)
    import student_report.config.settings as settings

    return importlib.reload(settings)


def test_env_example_contains_model_llm() -> None:
    expected = "MODEL_LLM=nvidia/nemotron-3.5-super-vl:free"
    assert expected in (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")


def test_default_model_used_when_env_var_absent(monkeypatch) -> None:
    settings = _reload_settings(monkeypatch, None)
    assert settings.LLM_MODEL == "nvidia/nemotron-3.5-super-vl:free"


def test_model_llm_read_from_env(monkeypatch) -> None:
    settings = _reload_settings(monkeypatch, "acme/other-model:free")
    assert settings.LLM_MODEL == "acme/other-model:free"


def test_dotenv_file_is_loaded(monkeypatch, tmp_path: Path) -> None:
    """El .env de la raíz del proyecto alimenta os.getenv.

    Se recarga settings tras apuntar temporalmente el .env a una copia
    de prueba con otro modelo, restaurándolo al final.
    """
    import shutil

    env_path = PROJECT_ROOT / ".env"
    backup = tmp_path / ".env.bak"
    had_original = env_path.exists()
    if had_original:
        shutil.copy(env_path, backup)
    try:
        env_path.write_text(
            "MODEL_LLM=from-dotenv/mock:free\n", encoding="utf-8"
        )
        monkeypatch.delenv("MODEL_LLM", raising=False)
        import student_report.config.settings as settings

        settings = importlib.reload(settings)
        assert settings.LLM_MODEL == "from-dotenv/mock:free"
    finally:
        if had_original:
            shutil.copy(backup, env_path)
        else:
            env_path.unlink(missing_ok=True)
        monkeypatch.delenv("MODEL_LLM", raising=False)
        importlib.reload(settings)


def test_client_and_pipeline_use_settings_model(monkeypatch) -> None:
    settings = _reload_settings(monkeypatch, None)
    from student_report.llm.client import OpenRouterClient
    from student_report.services.pipeline import PipelineConfig

    default_model = inspect.signature(
        OpenRouterClient.__init__).parameters["model"].default
    assert default_model == settings.LLM_MODEL
    assert inspect.signature(PipelineConfig).parameters["model"].default == (
        settings.LLM_MODEL
    )


def test_env_example_contains_required_external_parameters() -> None:
    text = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    for variable in (
        "MODEL_LLM=", "OPENROUTER_API_KEY=", "PASS_MARK=",
        "LOGO_ESCOLA=", "FOTO_ALUMNE=",
    ):
        assert variable in text
    assert "PASS_MARK=50.0" in text


def test_pass_mark_and_visual_settings_read_from_env(monkeypatch) -> None:
    monkeypatch.setenv("PASS_MARK", "60")
    monkeypatch.setenv("LOGO_ESCOLA", "https://exemple.cat/logo.png")
    monkeypatch.setenv("FOTO_ALUMNE", "https://exemple.cat/{student_id}.jpg")
    import student_report.config.settings as settings

    settings = importlib.reload(settings)
    assert settings.Pass_mark == 60.0
    assert settings.SCHOOL_LOGO_URL == "https://exemple.cat/logo.png"
    assert settings.STUDENT_PHOTO_URL_TEMPLATE == (
        "https://exemple.cat/{student_id}.jpg"
    )


def test_invalid_pass_mark_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.setenv("PASS_MARK", "no-es-un-numero")
    import student_report.config.settings as settings

    settings = importlib.reload(settings)
    assert settings.Pass_mark == settings.DEFAULT_PASS_MARK


def test_no_credentials_in_env_example() -> None:
    text = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY" in text  # placeholder seguro
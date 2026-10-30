"""Configuración estática: constantes, prompts y traducciones."""

from student_report.config.prompts import (
    JSON_SCHEMA_INSTRUCTIONS,
    LLM_INSTRUCTIONS,
    STATISTICAL_CONTEXT,
)
from student_report.config.settings import (
    DEFAULT_LANGUAGE,
    SKILLS,
    SKILLS_LOWER,
    SUPPORTED_LANGUAGES,
)
from student_report.config.translations import UI_TEXTS, get_ui_texts

__all__ = [
    "DEFAULT_LANGUAGE",
    "JSON_SCHEMA_INSTRUCTIONS",
    "LLM_INSTRUCTIONS",
    "SKILLS",
    "SKILLS_LOWER",
    "STATISTICAL_CONTEXT",
    "SUPPORTED_LANGUAGES",
    "UI_TEXTS",
    "get_ui_texts",
]

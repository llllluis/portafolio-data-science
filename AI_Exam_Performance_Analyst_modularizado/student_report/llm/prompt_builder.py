"""Construcción del prompt completo para el LLM."""

from __future__ import annotations

import json
from typing import Any

from student_report.config.prompts import (
    JSON_SCHEMA_INSTRUCTIONS,
    LLM_INSTRUCTIONS,
    STATISTICAL_CONTEXT,
)

__all__ = ["build_prompt"]


def build_prompt(student_profile: dict[str, Any], language: str) -> str:
    """Compone el prompt: instrucciones, contexto, perfil, esquema y
    las instrucciones finales con el idioma seleccionado.

    Args:
        student_profile: perfil devuelto por ``build_student_profile``.
        language: ``catala``, ``castellano`` o ``english``.
    """
    profile_json = json.dumps(student_profile, ensure_ascii=False, indent=2)

    return f"""
{LLM_INSTRUCTIONS}

CONTEXTO ESTADISTICO:
{STATISTICAL_CONTEXT}

PERFIL INDIVIDUAL DE ALUMNO:
{profile_json}

ESQUEMA JSON OBLIGATORIO:
{JSON_SCHEMA_INSTRUCTIONS}

FINAL OUTPUT INSTRUCTIONS

1. Write all pedagogical text in the selected language:
   {language}

2. The selected language applies to observations,
   skills balance, activity descriptions, procedures,
   and learning objectives.

3. Keep every JSON key exactly as defined in the schema.
   All JSON keys must remain in English.

4. Keep skill identifiers unchanged:
   grammar, listening, reading, speaking, writing.

5. The priority field must contain only:
   High, Medium, or Low.

6. Copy the student profile into student_data exactly.
   Do not modify or recalculate any profile values.

7. Return exactly one valid JSON object.
   Do not include Markdown, comments, or explanations
   outside the JSON object.
"""

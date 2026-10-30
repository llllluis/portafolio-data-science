"""Validación estructural y pedagógica del informe devuelto por el LLM."""

from __future__ import annotations

import math
from typing import Any

from student_report.config.settings import (
    MAX_ACTIVITIES,
    MIN_ACTIVITIES,
    SCORE_TOLERANCE,
    SKILLS_LOWER,
    VALID_PRIORITIES,
)
from student_report.core.exceptions import ReportValidationError

__all__ = ["validate_report_structure", "validate_pedagogical_coherence"]

_REQUIRED_KEYS: frozenset[str] = frozenset(
    {
        "student_data",
        "strengths",
        "areas_to_improve",
        "skills_balance",
        "proposed_activities",
    }
)
# (clave, tipo esperado, mensaje de error)
_TYPE_RULES: tuple[tuple[str, type, str], ...] = (
    ("student_data", dict, "'student_data' ha de ser un objecte."),
    ("strengths", list, "'strengths' ha de ser una llista."),
    ("areas_to_improve", list, "'areas_to_improve' ha de ser una llista."),
    ("skills_balance", str, "'skills_balance' ha de ser text."),
    ("proposed_activities", list, "'proposed_activities' ha de ser una llista."),
)
_EXACT_FIELDS: tuple[str, ...] = (
    "student_id",
    "evaluation_date",
    "best_skill",
    "weakest_skill",
)
_NUMERIC_FIELDS: tuple[str, ...] = ("average", "range")
_VALID_SKILLS: frozenset[str] = frozenset(SKILLS_LOWER)


def _close(a: Any, b: Any) -> bool:
    """Compara dos puntuaciones con la tolerancia del proyecto."""
    return math.isclose(float(a), float(b), abs_tol=SCORE_TOLERANCE)


def validate_report_structure(report: Any) -> None:
    """Comprueba claves obligatorias y tipos de primer nivel.

    Raises:
        ReportValidationError: al primer incumplimiento detectado.
    """
    if not isinstance(report, dict):
        raise ReportValidationError("L'informe no és un objecte JSON.")

    missing = set(_REQUIRED_KEYS) - set(report.keys())
    if missing:
        raise ReportValidationError(f"Falten claus obligatòries: {missing}")

    for key, expected_type, message in _TYPE_RULES:
        if not isinstance(report[key], expected_type):
            raise ReportValidationError(message)


def _check_student_data(returned: dict[str, Any], profile: dict[str, Any]) -> None:
    """Verifica que ``student_data`` reproduce el perfil original."""
    for field in _EXACT_FIELDS:
        if returned.get(field) != profile.get(field):
            raise ReportValidationError(
                f"Error en student_data: el camp '{field}' "
                "no coincideix amb el perfil original."
            )

    for field in _NUMERIC_FIELDS:
        if not _close(profile[field], returned[field]):
            raise ReportValidationError(
                f"Error en student_data: el camp '{field}' "
                "no coincideix amb el perfil original."
            )

    for skill, original_score in profile["skills"].items():
        returned_score = returned["skills"].get(skill)
        if returned_score is None or not _close(original_score, returned_score):
            raise ReportValidationError(
                f"Error: la nota de '{skill}' "
                "no coincideix amb el perfil original."
            )


def _check_skill_and_score(
    item: dict[str, Any], scores: dict[str, float], section: str
) -> float:
    """Valida la competencia y la nota de un elemento; devuelve la nota real."""
    skill = item["skill"]
    if skill not in _VALID_SKILLS:
        raise ReportValidationError(
            f"Competència no vàlida a {section}: {skill}"
        )
    real_score = float(scores[skill])
    if not math.isclose(real_score, float(item["score"]), abs_tol=SCORE_TOLERANCE):
        raise ReportValidationError(
            f"La nota de '{skill}' a {section} "
            "no coincideix amb les dades originals."
        )
    return real_score


def validate_pedagogical_coherence(
    report: dict[str, Any], profile: dict[str, Any]
) -> list[str]:
    """Valida la coherencia pedagógica del informe.

    Los errores graves lanzan excepción; las incoherencias leves se
    devuelven como lista de avisos (vacía si no hay ninguno).

    Raises:
        ReportValidationError: datos alterados, competencias o
            prioridades inválidas, o número de actividades fuera de rango.
    """
    _check_student_data(report["student_data"], profile)

    average = float(profile["average"])
    scores = profile["skills"]
    warnings: list[str] = []

    for strength in report["strengths"]:
        real = _check_skill_and_score(strength, scores, "strengths")
        if real < average:
            warnings.append(
                f"Revisa si '{strength['skill']}' és realment una fortalesa: "
                f"la seva nota ({real}) és inferior "
                f"a la mitjana ({average})."
            )

    for area in report["areas_to_improve"]:
        skill = area["skill"]
        real = _check_skill_and_score(area, scores, "areas_to_improve")
        if area["priority"] not in VALID_PRIORITIES:
            raise ReportValidationError(
                f"Prioritat no vàlida per a '{skill}': {area['priority']}"
            )
        if real >= average:
            warnings.append(
                f"Revisa si cal reforçar '{skill}': "
                f"la seva nota ({real}) no és inferior "
                f"a la mitjana ({average})."
            )

    activities = report["proposed_activities"]
    if not MIN_ACTIVITIES <= len(activities) <= MAX_ACTIVITIES:
        raise ReportValidationError(
            "L'informe ha de contenir entre 2 i 4 activitats."
        )

    improvement_skills = {area["skill"] for area in report["areas_to_improve"]}
    for activity in activities:
        skill = activity["skill"]
        if skill not in _VALID_SKILLS:
            raise ReportValidationError(
                f"Competència no vàlida en una activitat: {skill}"
            )
        if skill not in improvement_skills:
            warnings.append(
                f"L'activitat sobre '{skill}' no està associada "
                "a cap competència de areas_to_improve. "
                "Revisa si la proposta està justificada."
            )

    return warnings

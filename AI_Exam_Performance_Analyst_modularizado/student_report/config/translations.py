"""Textos de la interfaz del informe HTML en cada idioma soportado.

API pública: ``UI_TEXTS``, ``get_ui_texts``.
"""

from __future__ import annotations

from typing import Final

__all__ = ["UI_TEXTS", "get_ui_texts"]


UI_TEXTS: Final[dict[str, dict[str, str]]] = {
    "catala": {
        "title": "Informe de rendiment acadèmic",
        "subtitle": "Informe individual d'aprenentatge d'anglès",
        "student": "Alumne/a",
        "course": "Curs",
        "teacher": "Professor/a",
        "evaluation": "Avaluació",
        "school_year": "Any escolar",
        "student_id": "Identificador de l'alumne",
        "evaluation_date": "Data de l'avaluació",
        "results": "Resultats acadèmics",
        "average": "Mitjana",
        "result_final": "Resultat final",
        "pass_mark": "Llindar de superació",
        "result_unavailable": "Resultat no disponible",
        "skills": "Resultats per competència",
        "best": "Millor competència",
        "weakest": "Competència a reforçar",
        "strengths": "Punts forts",
        "improvements": "Aspectes a millorar",
        "priority": "Prioritat",
        "balance": "Equilibri entre competències",
        "activities": "Propostes d'activitats",
        "description": "Descripció",
        "procedure": "Com ho pots practicar",
        "objective": "Objectiu d'aprenentatge",
        "teacher_comment": "Comentari del professor",
        "teacher_comment_intro":
            "Observacions originals del professor sobre l'avaluació.",
        "ai_label": "Anàlisi pedagògica assistida per IA",
        "teacher_label": "Valoració del professor",
        "score": "Puntuació",
        "print": "Imprimir / Desar com a PDF",
        "footer": "Informe individual de seguiment acadèmic",
        "no_comment": "No hi ha cap comentari del professor registrat.",
        "no_data": "Informació no disponible",
        "no_strengths": "No s'han registrat punts forts.",
        "no_improvements": "No s'han registrat aspectes a millorar.",
        "no_activities": "No s'han proposat activitats.",
        "high": "Alta",
        "medium": "Mitjana",
        "low": "Baixa",
        "grammar": "Grammar",
        "listening": "Listening",
        "reading": "Reading",
        "speaking": "Speaking",
        "writing": "Writing",
    },

    "castellano": {
        "title": "Informe de rendimiento académico",
        "subtitle": "Informe individual de aprendizaje de inglés",
        "student": "Alumno/a",
        "course": "Curso",
        "teacher": "Profesor/a",
        "evaluation": "Evaluación",
        "school_year": "Año escolar",
        "student_id": "Identificador del alumno",
        "evaluation_date": "Fecha de evaluación",
        "results": "Resultados académicos",
        "average": "Media",
        "result_final": "Resultado final",
        "pass_mark": "Nota de aprobado",
        "result_unavailable": "Resultado no disponible",
        "skills": "Resultados por competencia",
        "best": "Mejor competencia",
        "weakest": "Competencia a reforzar",
        "strengths": "Puntos fuertes",
        "improvements": "Aspectos a mejorar",
        "priority": "Prioridad",
        "balance": "Equilibrio entre competencias",
        "activities": "Propuestas de actividades",
        "description": "Descripción",
        "procedure": "Cómo puedes practicarlo",
        "objective": "Objetivo de aprendizaje",
        "teacher_comment": "Comentario del profesor",
        "teacher_comment_intro":
            "Observaciones originales del profesor sobre la evaluación.",
        "ai_label": "Análisis pedagógico asistido por IA",
        "teacher_label": "Valoración del profesor",
        "score": "Puntuación",
        "print": "Imprimir / Guardar como PDF",
        "footer": "Informe individual de seguimiento académico",
        "no_comment": "No hay ningún comentario del profesor registrado.",
        "no_data": "Información no disponible",
        "no_strengths": "No se han registrado puntos fuertes.",
        "no_improvements": "No se han registrado aspectos a mejorar.",
        "no_activities": "No se han propuesto actividades.",
        "high": "Alta",
        "medium": "Media",
        "low": "Baja",
        "grammar": "Grammar",
        "listening": "Listening",
        "reading": "Reading",
        "speaking": "Speaking",
        "writing": "Writing",
    },

    "english": {
        "title": "Academic Performance Report",
        "subtitle": "Individual English Learning Report",
        "student": "Student",
        "course": "Course",
        "teacher": "Teacher",
        "evaluation": "Assessment",
        "school_year": "Academic year",
        "student_id": "Student ID",
        "evaluation_date": "Assessment date",
        "results": "Academic results",
        "average": "Average",
        "result_final": "Final result",
        "pass_mark": "Pass mark",
        "result_unavailable": "Result unavailable",
        "skills": "Results by skill",
        "best": "Strongest skill",
        "weakest": "Skill to develop",
        "strengths": "Strengths",
        "improvements": "Areas to improve",
        "priority": "Priority",
        "balance": "Balance across skills",
        "activities": "Suggested activities",
        "description": "Description",
        "procedure": "How to practise",
        "objective": "Learning objective",
        "teacher_comment": "Teacher's comment",
        "teacher_comment_intro":
            "Original teacher observations about the assessment.",
        "ai_label": "AI-assisted pedagogical analysis",
        "teacher_label": "Teacher's assessment",
        "score": "Score",
        "print": "Print / Save as PDF",
        "footer": "Individual academic progress report",
        "no_comment": "No teacher comment has been recorded.",
        "no_data": "Information not available",
        "no_strengths": "No strengths have been recorded.",
        "no_improvements": "No areas for improvement have been recorded.",
        "no_activities": "No activities have been suggested.",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "grammar": "Grammar",
        "listening": "Listening",
        "reading": "Reading",
        "speaking": "Speaking",
        "writing": "Writing",
    }
}


def get_ui_texts(language: str) -> dict[str, str]:
    """Devuelve el diccionario de textos de la interfaz para ``language``.

    Raises:
        ValueError: si el idioma no está soportado.
    """
    if language not in UI_TEXTS:
        raise ValueError(
            f"Idioma no vàlid: {language}. "
            "Utilitza catala, castellano o english."
        )
    return UI_TEXTS[language]
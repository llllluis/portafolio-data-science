"""Cálculo del perfil del alumno: notas, media, mejor/peor y rango."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from student_report.config.settings import ANALYSIS_COLUMNS, SKILLS

__all__ = [
    "EvaluationKeys",
    "get_evaluation_keys",
    "build_analysis_frame",
    "build_student_profile",
]


@dataclass(frozen=True)
class EvaluationKeys:
    """Identificadores de la evaluación y del curso de un alumno."""

    evaluation_id: int
    course_id: Any


def get_evaluation_keys(df_student: pd.DataFrame) -> EvaluationKeys:
    """Extrae ``IDEVALUACIO`` (int) e ``IDCURS`` de la primera fila."""
    return EvaluationKeys(
        evaluation_id=int(df_student["IDEVALUACIO"].iloc[0]),
        course_id=df_student["IDCURS"].iloc[0],
    )


def build_analysis_frame(
    df_student: pd.DataFrame,
    student_id: Any,
    evaluation_date: pd.Timestamp,
    keys: EvaluationKeys,
) -> pd.DataFrame:
    """Construye el DataFrame de análisis (una fila) del alumno.

    Columnas resultantes, en este orden: ``IDALUMNE``, ``DATA``,
    ``IDEVALUACIO``, ``IDCURS``, las cinco competencias, ``Average``,
    ``Best``, ``Worst`` y ``RANG``.
    """
    skills = list(SKILLS)

    analysis = (
        df_student.set_index("MATERIA")["PERCENTATGE"]
        .reindex(skills)  # fuerza las 5 materias y su orden
        .to_frame()
        .T
    )
    analysis.columns.name = None

    analysis.insert(0, "IDALUMNE", student_id)
    analysis.insert(1, "DATA", evaluation_date)
    analysis.insert(2, "IDEVALUACIO", keys.evaluation_id)
    analysis.insert(3, "IDCURS", keys.course_id)

    scores = analysis[skills]
    analysis["Average"] = scores.mean(axis=1)
    analysis["Best"] = scores.idxmax(axis=1)
    analysis["Worst"] = scores.idxmin(axis=1)
    analysis["RANG"] = scores.max(axis=1) - scores.min(axis=1)

    return analysis[list(ANALYSIS_COLUMNS)]


def build_student_profile(analysis: pd.DataFrame) -> dict[str, Any]:
    """Convierte la primera fila del análisis en el perfil para el LLM."""
    row = analysis.iloc[0]
    return {
        "student_id": int(row["IDALUMNE"]),
        "evaluation_date": row["DATA"].strftime("%Y-%m-%d"),
        "skills": {skill.lower(): float(row[skill]) for skill in SKILLS},
        "average": round(float(row["Average"]), 2),
        "best_skill": str(row["Best"]).lower(),
        "weakest_skill": str(row["Worst"]).lower(),
        "range": round(float(row["RANG"]), 2),
    }

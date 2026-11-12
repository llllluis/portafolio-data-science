"""Carga, normalización y localización del CSV de resultados.

El registro de un alumno se localiza por la combinación de los tres
identificadores ``IDALUMNE + IDEVALUACIO + IDCURS``. La fecha de la
evaluación (``DATA``) ya NO se recibe por línea de comandos: se lee del
propio registro encontrado en el CSV.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from student_report.config.settings import (
    REQUIRED_RESULTS_COLUMNS,
    RESULTS_CSV_PATH,
    SKILLS,
)
from student_report.core.exceptions import (
    DataValidationError,
    MultipleRecordsFoundError,
    NoRecordsFoundError,
)
from student_report.utils.ids import normalize_id, normalize_scalar_id
from student_report.utils.io import ensure_file_exists, read_semicolon_csv

__all__ = [
    "load_results",
    "normalize_results",
    "parse_evaluation_date",
    "validate_results_columns",
    "filter_student_results",
    "ensure_not_empty",
    "ensure_unique_skills",
    "ensure_all_skills_present",
    "resolve_evaluation_date",
    "describe_ids",
]


def describe_ids(student_id: Any, evaluation_id: Any, course_id: Any) -> str:
    """Texto único con los tres identificadores, para los mensajes de error."""
    return (
        f"IDALUMNE={student_id}, IDEVALUACIO={evaluation_id}, "
        f"IDCURS={course_id}"
    )


def validate_results_columns(df: pd.DataFrame) -> None:
    """Comprueba que el CSV de resultados contiene las columnas necesarias.

    Raises:
        DataValidationError: si falta alguna columna obligatoria.
    """
    missing = [c for c in REQUIRED_RESULTS_COLUMNS if c not in df.columns]
    if missing:
        raise DataValidationError(
            "Faltan columnas obligatorias en el CSV de resultados "
            f"(RESULTS_CSV_PATH): {', '.join(missing)}. "
            f"Columnas encontradas: {', '.join(map(str, df.columns))}."
        )


def load_results(path: str | Path = RESULTS_CSV_PATH) -> pd.DataFrame:
    """Lee el CSV principal de notas parciales ponderadas.

    Raises:
        FileNotFoundError: si el fichero no existe.
        DataValidationError: si faltan columnas obligatorias.
    """
    ensure_file_exists(
        path,
        "No se encuentra el CSV de resultados en: {path}. "
        "Revisa la variable RESULTS_CSV_PATH del .env.",
    )
    df = read_semicolon_csv(path)
    validate_results_columns(df)
    return df


def normalize_results(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos: ``IDALUMNE`` texto, ``MATERIA`` en mayúsculas
    y ``DATA`` como fecha sin hora. Modifica y devuelve ``df``.

    ``DATA`` inválida se convierte en ``NaT``; la validación posterior
    (:func:`resolve_evaluation_date`) es la que informa del problema.
    """
    df["IDALUMNE"] = df["IDALUMNE"].astype(str).str.strip()
    df["MATERIA"] = df["MATERIA"].astype(str).str.strip().str.upper()
    df["DATA"] = pd.to_datetime(
        df["DATA"], errors="coerce", dayfirst=True
    ).dt.normalize()
    return df


def parse_evaluation_date(value: str) -> pd.Timestamp:
    """Convierte una fecha (``YYYY-MM-DD`` o ``dd/mm/aaaa``) en ``Timestamp``.

    Se conserva por compatibilidad: el pipeline ya NO la usa para
    identificar el registro, solo se obtiene la fecha del CSV.
    """
    return pd.to_datetime(value, dayfirst=True).normalize()


def filter_student_results(
    df: pd.DataFrame,
    student_id: Any,
    evaluation_id: Any,
    course_id: Any,
) -> pd.DataFrame:
    """Devuelve una copia con las filas de la combinación indicada.

    Los tres identificadores se comparan normalizados como texto, de
    modo que ``7``, ``"7"`` y ``7.0`` se consideran el mismo valor.
    No lanza error si el resultado está vacío: ver
    :func:`ensure_not_empty`.
    """
    mask = (
        (normalize_id(df["IDALUMNE"]) == normalize_scalar_id(student_id))
        & (
            normalize_id(df["IDEVALUACIO"])
            == normalize_scalar_id(evaluation_id)
        )
        & (normalize_id(df["IDCURS"]) == normalize_scalar_id(course_id))
    )
    return df[mask.fillna(False).astype(bool)].copy()


def ensure_not_empty(
    df: pd.DataFrame, student_id: Any, evaluation_id: Any, course_id: Any
) -> None:
    """Lanza :class:`NoRecordsFoundError` si ``df`` está vacío."""
    if df.empty:
        raise NoRecordsFoundError(
            "⚠️ No hay ningún registro en el CSV de resultados para "
            f"{describe_ids(student_id, evaluation_id, course_id)}."
        )


def ensure_unique_skills(
    df: pd.DataFrame, student_id: Any, evaluation_id: Any, course_id: Any
) -> None:
    """Comprueba que cada habilidad aparece una sola vez.

    Una combinación ``IDALUMNE + IDEVALUACIO + IDCURS`` contiene
    legítimamente cinco filas (una por ``MATERIA``). Un duplicado es la
    misma ``MATERIA`` repetida dentro de esa combinación.

    Raises:
        MultipleRecordsFoundError: si hay habilidades repetidas.
    """
    duplicated = df["MATERIA"][df["MATERIA"].duplicated(keep=False)]
    if not duplicated.empty:
        repeated = ", ".join(sorted(set(duplicated)))
        raise MultipleRecordsFoundError(
            "Hay varios registros para la misma combinación "
            f"({describe_ids(student_id, evaluation_id, course_id)}). "
            f"Habilidades repetidas: {repeated}. No se selecciona "
            "ningún registro automáticamente."
        )


def ensure_all_skills_present(
    df: pd.DataFrame, student_id: Any, evaluation_id: Any, course_id: Any
) -> None:
    """Comprueba que están las cinco competencias del análisis.

    Raises:
        DataValidationError: si falta alguna de las cinco habilidades.
    """
    present = set(df["MATERIA"])
    missing = [skill for skill in SKILLS if skill not in present]
    if missing:
        raise DataValidationError(
            "Faltan habilidades en el CSV de resultados para "
            f"{describe_ids(student_id, evaluation_id, course_id)}: "
            f"{', '.join(missing)}."
        )


def resolve_evaluation_date(
    df: pd.DataFrame, student_id: Any, evaluation_id: Any, course_id: Any
) -> pd.Timestamp:
    """Obtiene la fecha de evaluación a partir del registro del CSV.

    Raises:
        DataValidationError: si ``DATA`` está vacía, no es una fecha
            válida o las filas de la combinación no comparten la misma
            fecha.
    """
    dates = pd.Series(df["DATA"].dropna().unique())
    if dates.empty:
        raise DataValidationError(
            "La fecha (DATA) del registro "
            f"({describe_ids(student_id, evaluation_id, course_id)}) "
            "está vacía o no tiene un formato válido (dd/mm/aaaa)."
        )
    if len(dates) > 1:
        formatted = ", ".join(
            pd.Timestamp(value).date().isoformat() for value in dates
        )
        raise DataValidationError(
            "El registro "
            f"({describe_ids(student_id, evaluation_id, course_id)}) "
            f"tiene fechas distintas en el CSV: {formatted}. "
            "Corrige el dato antes de generar el informe."
        )
    return pd.Timestamp(dates.iloc[0]).normalize()

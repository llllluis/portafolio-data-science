"""Carga, normalización y filtrado del CSV de resultados."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from student_report.config.settings import RESULTS_CSV_PATH
from student_report.core.exceptions import NoRecordsFoundError
from student_report.utils.io import ensure_file_exists, read_semicolon_csv

__all__ = [
    "load_results",
    "normalize_results",
    "parse_evaluation_date",
    "filter_student_results",
    "ensure_not_empty",
]


def load_results(path: str | Path = RESULTS_CSV_PATH) -> pd.DataFrame:
    """Lee el CSV principal de notas parciales ponderadas.

    Raises:
        FileNotFoundError: si el fichero no existe.
    """
    ensure_file_exists(path, "No s'ha trobat el fitxer principal: {path}")
    return read_semicolon_csv(path)


def normalize_results(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos: ``IDALUMNE`` texto, ``MATERIA`` en mayúsculas
    y ``DATA`` como fecha sin hora. Modifica y devuelve ``df``."""
    df["IDALUMNE"] = df["IDALUMNE"].astype(str).str.strip()
    df["MATERIA"] = df["MATERIA"].astype(str).str.strip().str.upper()
    df["DATA"] = pd.to_datetime(
        df["DATA"], errors="coerce", dayfirst=True
    ).dt.normalize()
    return df


def parse_evaluation_date(value: str) -> pd.Timestamp:
    """Convierte la fecha recibida (``YYYY-MM-DD``) en ``Timestamp`` normalizado."""
    return pd.to_datetime(value, dayfirst=True).normalize()


def filter_student_results(
    df: pd.DataFrame,
    student_id: str,
    evaluation_date: pd.Timestamp,
) -> pd.DataFrame:
    """Devuelve una copia con las filas del alumno en la fecha indicada.

    No lanza error si está vacío: ver :func:`ensure_not_empty`.
    """
    return df[
        (df["IDALUMNE"] == student_id) & (df["DATA"] == evaluation_date)
    ].copy()


def ensure_not_empty(
    df: pd.DataFrame, student_id: str, evaluation_date: pd.Timestamp
) -> None:
    """Lanza :class:`NoRecordsFoundError` si ``df`` está vacío."""
    if df.empty:
        raise NoRecordsFoundError(
            f"⚠️ Cap registre per IDALUMNE={student_id} "
            f"i DATA={evaluation_date.date()}"
        )

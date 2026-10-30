"""Datos complementarios del alumno (nombre, curso, profesor, comentario)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from student_report.config.settings import EXTRA_INFO_COLUMNS, EXTRA_INFO_CSV_PATH
from student_report.core.exceptions import ExtraInfoError
from student_report.utils.ids import normalize_id, normalize_scalar_id
from student_report.utils.io import ensure_file_exists, read_semicolon_csv

__all__ = ["load_extra_info", "merge_extra_info", "build_report_context"]

_ID_COLUMNS: tuple[str, ...] = ("IDALUMNE", "IDEVALUACIO", "IDCURS")
_MERGE_KEYS: list[str] = [f"_{column}_CLAU" for column in _ID_COLUMNS]

# Columna del CSV -> clave usada por el renderizador HTML.
_CONTEXT_FIELDS: dict[str, str] = {
    "student_name": "NOM_ALUMNE",
    "teacher": "PROFE",
    "course": "NOMCURS",
    "evaluation_description": "DESCRIPCIO",
    "school_year": "EJERCICIO_ESCOLAR",
    "teacher_comment": "COMENTARI",
}


def load_extra_info(path: str | Path = EXTRA_INFO_CSV_PATH) -> pd.DataFrame:
    """Lee el CSV complementario y devuelve solo las columnas necesarias.

    Raises:
        FileNotFoundError: si no existe el fichero.
        ExtraInfoError: si faltan columnas obligatorias.
    """
    ensure_file_exists(path, "No s'ha trobat el fitxer complementari: {path}")
    df = read_semicolon_csv(path)

    missing = [c for c in EXTRA_INFO_COLUMNS if c not in df.columns]
    if missing:
        raise ExtraInfoError(
            f"Falten columnes al fitxer complementari: {missing}"
        )
    return df[list(EXTRA_INFO_COLUMNS)].copy()


def _add_merge_keys(df: pd.DataFrame) -> None:
    """Añade in-place las columnas de clave normalizadas."""
    for column, key in zip(_ID_COLUMNS, _MERGE_KEYS, strict=True):
        df[key] = normalize_id(df[column])


def _check_keys(df_extra: pd.DataFrame) -> None:
    """Verifica que las claves del complementario no estén vacías ni duplicadas."""
    if df_extra[_MERGE_KEYS].isna().any().any():
        raise ExtraInfoError(
            "Hi ha identificadors buits al fitxer complementari."
        )
    if df_extra[_MERGE_KEYS].eq("").any().any():  # type: ignore[arg-type]
        raise ExtraInfoError(
            "Hi ha identificadors buits al fitxer complementari."
        )
    if df_extra.duplicated(_MERGE_KEYS).any():
        raise ExtraInfoError(
            "Hi ha combinacions duplicades d'IDALUMNE, "
            "IDEVALUACIO i IDCURS al fitxer complementari."
        )


def merge_extra_info(
    analysis: pd.DataFrame, df_extra: pd.DataFrame
) -> tuple[pd.DataFrame, int]:
    """Une el análisis con los datos complementarios (left join).

    Ninguno de los DataFrames de entrada se modifica.

    Returns:
        Tupla ``(df_final, filas_sin_info)``.
    """
    left = analysis.copy()
    right = df_extra.copy()
    _add_merge_keys(left)
    _add_merge_keys(right)
    _check_keys(right)

    merged = left.merge(
        right.drop(columns=list(_ID_COLUMNS)),
        on=_MERGE_KEYS,
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    rows_without_info = int((merged["_merge"] == "left_only").sum())
    merged.drop(columns=_MERGE_KEYS + ["_merge"], inplace=True)
    return merged, rows_without_info


def build_report_context(
    df_final: pd.DataFrame, student_id: str, evaluation_id: int
) -> dict[str, Any]:
    """Extrae los datos de cabecera del informe HTML para el alumno.

    Raises:
        ExtraInfoError: si no se encuentra la fila del alumno/evaluación.
    """
    row = df_final[
        (normalize_id(df_final["IDALUMNE"]) == normalize_scalar_id(student_id))
        & (
            normalize_id(df_final["IDEVALUACIO"])
            == normalize_scalar_id(evaluation_id)
        )
    ]
    if row.empty:
        raise ExtraInfoError(
            "No s'han trobat les dades de l'alumne i l'avaluació "
            "a df_informe_final."
        )
    first = row.iloc[0]
    return {key: first[column] for key, column in _CONTEXT_FIELDS.items()}

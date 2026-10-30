"""Entrada/salida de ficheros: CSV.

Nota v9: la respuesta JSON del LLM se conserva únicamente en memoria
(validación y generación del HTML). Este módulo ya NO guarda ficheros
JSON en disco.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from student_report.config.settings import CSV_READ_OPTIONS

__all__ = ["ensure_file_exists", "read_semicolon_csv"]


def ensure_file_exists(path: str | Path, message: str) -> Path:
    """Comprueba que ``path`` existe y es un fichero.

    Args:
        path: ruta a comprobar.
        message: texto del error; ``{path}`` se sustituye por la ruta.

    Raises:
        FileNotFoundError: si el fichero no existe.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(message.format(path=path))
    return file_path


def read_semicolon_csv(path: str | Path) -> pd.DataFrame:
    """Lee un CSV con separador ``;``, decimal ``,`` y BOM UTF-8."""
    return pd.read_csv(
        path,
        sep=CSV_READ_OPTIONS["sep"],
        encoding=CSV_READ_OPTIONS["encoding"],
        decimal=CSV_READ_OPTIONS["decimal"],
    )
"""Entrada/salida de ficheros: CSV.

Nota v9: la respuesta JSON del LLM se conserva únicamente en memoria
(validación y generación del HTML). Este módulo ya NO guarda ficheros
JSON en disco.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from student_report.config.settings import CSV_READ_OPTIONS

__all__ = ["ensure_file_exists", "ensure_source_csvs", "read_semicolon_csv"]


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


def ensure_source_csvs(
    results_path: str | Path, extra_info_path: str | Path
) -> None:
    """Comprueba que existan los dos CSV de origen configurados en el ``.env``.

    Se valida antes de empezar el pipeline para dar un error único y
    claro (variable de entorno + ruta resuelta) en lugar de un
    ``FileNotFoundError`` a mitad del proceso.

    Raises:
        FileNotFoundError: si alguna ruta no es un fichero existente.
    """
    for env_name, path in (
        ("RESULTS_CSV_PATH", results_path),
        ("EXTRA_INFO_CSV_PATH", extra_info_path),
    ):
        target = Path(path)
        if not target.is_file():
            raise FileNotFoundError(
                f"No se encuentra el fichero configurado en {env_name}: "
                f"{target}. Comprueba la ruta en el .env (las rutas "
                "relativas se resuelven respecto al directorio del "
                "proyecto, el que contiene main.py)."
            )


def read_semicolon_csv(path: str | Path) -> pd.DataFrame:
    """Lee un CSV con separador ``;``, decimal ``,`` y BOM UTF-8."""
    return pd.read_csv(
        path,
        sep=CSV_READ_OPTIONS["sep"],
        encoding=CSV_READ_OPTIONS["encoding"],
        decimal=CSV_READ_OPTIONS["decimal"],
    )
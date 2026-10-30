"""Normalización de identificadores para cruces entre DataFrames."""

from __future__ import annotations

from typing import Any

import pandas as pd

__all__ = ["normalize_id", "normalize_scalar_id"]


def normalize_id(series: pd.Series) -> pd.Series:
    """Normaliza una serie de identificadores a texto comparable.

    Convierte a ``string``, elimina espacios y el sufijo ``.0`` que
    aparece cuando pandas lee un entero como ``float``.
    """
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


def normalize_scalar_id(value: Any) -> Any:
    """Aplica :func:`normalize_id` a un único valor."""
    return normalize_id(pd.Series([value])).iloc[0]

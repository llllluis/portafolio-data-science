"""Funciones auxiliares de escape y formato para HTML."""

from __future__ import annotations

import html
import math
from typing import Any

__all__ = ["escape_html", "clamp_score", "format_score"]


def escape_html(value: Any) -> str:
    """Escapa ``value`` para insertarlo de forma segura en HTML.

    ``None`` y ``NaN`` se convierten en cadena vacía; el resto se
    convierte a texto, se recorta y se escapa.
    """
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return html.escape(str(value).strip())


def clamp_score(value: Any) -> float:
    """Convierte una puntuación a ``float`` acotado a [0, 100].

    Valores no numéricos o no finitos devuelven ``0.0``.
    """
    try:
        result = float(value)
        if not math.isfinite(result):
            return 0.0
        return max(0.0, min(100.0, result))
    except (TypeError, ValueError):
        return 0.0


def format_score(value: Any) -> str:
    """Formatea una puntuación con hasta 2 decimales sin ceros finales."""
    return f"{clamp_score(value):.2f}".rstrip("0").rstrip(".")

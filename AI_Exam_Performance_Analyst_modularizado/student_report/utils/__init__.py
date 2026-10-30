"""Utilidades genéricas sin dependencias del dominio."""

from student_report.utils.html_utils import clamp_score, escape_html, format_score
from student_report.utils.ids import normalize_id, normalize_scalar_id
from student_report.utils.io import ensure_file_exists, read_semicolon_csv

__all__ = [
    "clamp_score",
    "ensure_file_exists",
    "escape_html",
    "format_score",
    "normalize_id",
    "normalize_scalar_id",
    "read_semicolon_csv",
]
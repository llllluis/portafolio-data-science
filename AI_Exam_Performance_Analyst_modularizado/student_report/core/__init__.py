"""Lógica de dominio: carga de datos, perfil del alumno y validación."""

from student_report.core.analysis import (
    EvaluationKeys,
    build_analysis_frame,
    build_student_profile,
    get_evaluation_keys,
)
from student_report.core.data_loader import (
    ensure_not_empty,
    filter_student_results,
    load_results,
    normalize_results,
    parse_evaluation_date,
)
from student_report.core.exceptions import (
    ExtraInfoError,
    LLMReportError,
    NoRecordsFoundError,
    ReportValidationError,
    StudentReportError,
)
from student_report.core.extra_info import (
    build_report_context,
    load_extra_info,
    merge_extra_info,
)
from student_report.core.validation import (
    validate_pedagogical_coherence,
    validate_report_structure,
)

__all__ = [
    "EvaluationKeys",
    "ExtraInfoError",
    "LLMReportError",
    "NoRecordsFoundError",
    "ReportValidationError",
    "StudentReportError",
    "build_analysis_frame",
    "build_report_context",
    "build_student_profile",
    "ensure_not_empty",
    "filter_student_results",
    "get_evaluation_keys",
    "load_extra_info",
    "load_results",
    "merge_extra_info",
    "normalize_results",
    "parse_evaluation_date",
    "validate_pedagogical_coherence",
    "validate_report_structure",
]

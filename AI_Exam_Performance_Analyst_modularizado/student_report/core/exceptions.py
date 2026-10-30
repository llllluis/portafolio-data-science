"""Jerarquía de excepciones del paquete.

Las excepciones de validación heredan de ``ValueError`` para que el
código que ya capturaba ``ValueError`` siga funcionando igual.
"""

from __future__ import annotations

__all__ = [
    "StudentReportError",
    "NoRecordsFoundError",
    "ReportValidationError",
    "ExtraInfoError",
    "LLMReportError",
]


class StudentReportError(Exception):
    """Clase base de todos los errores propios del paquete."""


class NoRecordsFoundError(StudentReportError, LookupError):
    """No hay registros para el alumno y la fecha indicados."""


class ReportValidationError(StudentReportError, ValueError):
    """El informe devuelto por el LLM no cumple el esquema o es incoherente."""


class ExtraInfoError(StudentReportError, ValueError):
    """El fichero complementario es inválido o no contiene al alumno."""


class LLMReportError(StudentReportError, RuntimeError):
    """No se ha podido obtener un informe JSON válido del LLM."""

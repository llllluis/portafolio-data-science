"""Interfaz de línea de comandos.

Argumentos (identificación por tres claves):

- ``--idalumne``: identificador del alumno (obligatorio).
- ``--idevaluacio``: identificador de la evaluación (obligatorio).
- ``--idcurs``: identificador del curso (obligatorio).
- ``--language``: código ISO 639-1 ``ca`` | ``es`` | ``en``, con
  ``en`` por defecto si se omite (se aceptan también los nombres
  internos ``catala``, ``castellano`` y ``english`` por compatibilidad).
- ``--analisis-ia``: ``true`` | ``false``. Por defecto ``true``: activa
  el análisis pedagógico mediante el LLM. Con ``false`` no se llama al
  LLM y el informe se genera solo con los resultados académicos.

La fecha de la evaluación ya NO se recibe por consola: se obtiene del
registro localizado en el CSV de resultados (columna ``DATA``).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Sequence
from typing import NoReturn

from student_report.config.settings import (
    DEFAULT_LANGUAGE_CODE,
    INTERNAL_LANGUAGE_CODES,
    LANGUAGE_CODES,
    SUPPORTED_LANGUAGES,
    normalize_language,
)
from student_report.core.exceptions import (
    DataValidationError,
    ExtraInfoError,
    MultipleRecordsFoundError,
    NoRecordsFoundError,
)
from student_report.services.pipeline import (
    PipelineConfig,
    PipelineResult,
    run_pipeline,
)

__all__ = [
    "SpanishArgumentParser",
    "build_parser",
    "parse_bool",
    "parse_course_id",
    "parse_args",
    "main",
]

# Mensajes internos de argparse traducidos al castellano.
_ARGPARSE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"^the following arguments are required: (.+)$",
     r"faltan los siguientes argumentos obligatorios: \1"),
    (r"^unrecognized arguments: (.+)$",
     r"argumentos no reconocidos: \1"),
    (r"^argument (\S+): invalid choice: (.*)$",
     r"argumento \1: opción no válida: \2"),
    (r"^argument (\S+): invalid int value: (.*)$",
     r"argumento \1: valor entero no válido: \2"),
    (r"^argument (\S+): expected one argument$",
     r"argumento \1: se esperaba un valor"),
    (r"^argument (\S+): invalid value: (.*)$",
     r"argumento \1: valor no válido: \2"),
)

_HELP_SECTIONS: tuple[tuple[str, str], ...] = (
    ("usage: ", "uso: "),
    ("positional arguments:", "argumentos posicionales:"),
    ("options:", "opciones:"),
)


class SpanishArgumentParser(argparse.ArgumentParser):
    """``ArgumentParser`` con la ayuda y los errores en castellano."""

    def format_help(self) -> str:
        text = super().format_help()
        for source, target in _HELP_SECTIONS:
            text = text.replace(source, target)
        return text

    def format_usage(self) -> str:
        return super().format_usage().replace("usage: ", "uso: ")

    def error(self, message: str) -> NoReturn:  # type: ignore[override]
        translated = message
        for pattern, replacement in _ARGPARSE_PATTERNS:
            if re.match(pattern, message):
                translated = re.sub(pattern, replacement, message)
                break
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {translated}\n")


def parse_bool(value: str) -> bool:
    """Convierte el valor de ``--analisis-ia`` en ``bool``.

    Solo acepta ``true`` y ``false`` (insensible a mayúsculas).

    Raises:
        argparse.ArgumentTypeError: con cualquier otro valor.
    """
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("El valor ha de ser true o false.")


def parse_course_id(value: str) -> int | str:
    """Convierte ``--idcurs`` en ``int`` si es numérico; si no, en texto.

    Permite cursos con identificador numérico (``7``) y también
    alfanumérico (``A2-GEN``) sin cambiar el resto del pipeline.
    """
    text = value.strip()
    if text.lstrip("+-").isdigit():
        return int(text)
    return text


def build_parser() -> argparse.ArgumentParser:
    """Crea el parser con los argumentos de identificación actuales."""
    parser = SpanishArgumentParser(
        description="Analiza los resultados de un alumno.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="muestra este mensaje de ayuda y sale",
    )
    parser.add_argument("--idalumne", type=int, required=True,
                        help="ID del alumno")
    parser.add_argument("--idevaluacio", type=int, required=True,
                        help="ID de la evaluación")
    parser.add_argument("--idcurs", type=parse_course_id, required=True,
                        help="ID del curso")
    parser.add_argument(
        "--language",
        type=str,
        choices=[*LANGUAGE_CODES, *SUPPORTED_LANGUAGES],
        default=DEFAULT_LANGUAGE_CODE,
        help=(
            "Idioma del informe según ISO 639-1: "
            "ca (catalán), es (castellano), en (inglés). "
            "Por defecto: en (inglés)"
        ),
    )
    parser.add_argument(
        "--analisis-ia",
        type=parse_bool,
        default=True,
        metavar="{true,false}",
        help=(
            "Activa o desactiva el análisis con IA "
            "(por defecto: true)"
        ),
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> PipelineConfig:
    """Convierte los argumentos de consola en un :class:`PipelineConfig`.

    La conversión del código ISO 639-1 al idioma interno se hace con la
    función centralizada :func:`student_report.config.settings.normalize_language`.
    """
    args = build_parser().parse_args(argv)
    return PipelineConfig(
        student_id=args.idalumne,
        evaluation_id=args.idevaluacio,
        course_id=args.idcurs,
        language=normalize_language(args.language),
        ai_analysis=args.analisis_ia,
    )


def main(argv: Sequence[str] | None = None) -> PipelineResult:
    """Punto de entrada de consola.

    Los errores de localización o de configuración terminan con
    ``SystemExit`` y un mensaje legible (sin traza de Python).
    """
    config = parse_args(argv)
    try:
        return run_pipeline(config)
    except (
        NoRecordsFoundError,
        MultipleRecordsFoundError,
        DataValidationError,
        ExtraInfoError,
        FileNotFoundError,
    ) as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()

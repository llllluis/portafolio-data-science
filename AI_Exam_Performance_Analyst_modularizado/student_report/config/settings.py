"""Constantes de configuración del proyecto.

Centraliza rutas, nombres de columnas, competencias, idiomas y
parámetros del LLM que en la versión original estaban dispersos
como literales a lo largo del script.

Además carga la configuración de la raíz del proyecto desde el
fichero ``.env`` (que sustituye al antiguo ``config.py``):
``PASS_MARK``, ``LOGO_ESCOLA``, ``FOTO_ALUMNE`` y ``MODEL_LLM``.
Si una variable no está definida, se usa el valor por defecto
definido aquí.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Final

__all__ = [
    "RESULTS_CSV_PATH",
    "EXTRA_INFO_CSV_PATH",
    "OUTPUT_DIR",
    "BASE_CSS_PATH",
    "REPORT_CSS_FILENAME",
    "REPORT_CSS_ASSET",
    "CSV_READ_OPTIONS",
    "SKILLS",
    "SKILLS_LOWER",
    "ANALYSIS_COLUMNS",
    "EXTRA_INFO_COLUMNS",
    "SUPPORTED_LANGUAGES",
    "DEFAULT_LANGUAGE",
    "LANGUAGE_CODES",
    "INTERNAL_LANGUAGE_CODES",
    "DEFAULT_LANGUAGE_CODE",
    "LANGUAGE_CODES_INTERNAL",
    "Pass_mark",
    "SCHOOL_LOGO_URL",
    "STUDENT_PHOTO_URL_TEMPLATE",
    "REPORT_SCHOOL_NAME",
    "VALID_PRIORITIES",
    "MIN_ACTIVITIES",
    "MAX_ACTIVITIES",
    "SCORE_TOLERANCE",
    "OPENROUTER_BASE_URL",
    "OPENROUTER_API_KEY_ENV",
    "MODEL_LLM_ENV",
    "DEFAULT_LLM_MODEL",
    "PASS_MARK_ENV",
    "DEFAULT_PASS_MARK",
    "LOGO_ESCOLA_ENV",
    "FOTO_ALUMNE_ENV",
    "LLM_MODEL",
    "LLM_EXTRA_BODY",
]


# ------------------------------------------------------------------
# Fichero .env (raíz del proyecto)
# ------------------------------------------------------------------

def _load_env_file() -> None:
    """Carga el ``.env`` de la raíz del proyecto en el entorno.

    No sobrescribe variables que ya existan en el entorno real
    (``override=False``). Si ``python-dotenv`` no está instalado o el
    fichero no existe, simplemente no hace nada.
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(env_path, override=False)


_load_env_file()

# ------------------------------------------------------------------
# Rutas (relativas al directorio de trabajo, como en el original)
# ------------------------------------------------------------------
RESULTS_CSV_PATH: Final[str] = "data/NOTA_PARCIAL_PONDERADA_ALUMN.csv"
EXTRA_INFO_CSV_PATH: Final[str] = (
    "data/INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv"
)
OUTPUT_DIR: Final[str] = "reports"
BASE_CSS_PATH: Final[str] = "style.css"
REPORT_CSS_FILENAME: Final[str] = "informe.css"
REPORT_CSS_ASSET: Final[Path] = (
    Path(__file__).resolve().parent.parent / "reports" / "assets" / "report.css"
)

# Opciones comunes de lectura de los CSV de origen.
CSV_READ_OPTIONS: Final[dict[str, str]] = {
    "sep": ";",
    "encoding": "utf-8-sig",
    "decimal": ",",
}

# ------------------------------------------------------------------
# Competencias y columnas
# ------------------------------------------------------------------
SKILLS: Final[tuple[str, ...]] = (
    "GRAMMAR",
    "LISTENING",
    "READING",
    "SPEAKING",
    "WRITING",
)
SKILLS_LOWER: Final[tuple[str, ...]] = tuple(s.lower() for s in SKILLS)

ANALYSIS_COLUMNS: Final[tuple[str, ...]] = (
    "IDALUMNE",
    "DATA",
    "IDEVALUACIO",
    "IDCURS",
    *SKILLS,
    "Average",
    "Best",
    "Worst",
    "RANG",
)

EXTRA_INFO_COLUMNS: Final[tuple[str, ...]] = (
    "IDALUMNE",
    "IDEVALUACIO",
    "IDCURS",
    "COMENTARI",
    "PROFE",
    "NOMCURS",
    "NOM_ALUMNE",
    "DESCRIPCIO",
    "EJERCICIO_ESCOLAR",
)

# ------------------------------------------------------------------
# Idiomas
# ------------------------------------------------------------------
# Idiomas internos del paquete (nombres usados en el prompt del LLM,
# en las traducciones y en la validación).
SUPPORTED_LANGUAGES: Final[tuple[str, ...]] = ("catala", "castellano", "english")
DEFAULT_LANGUAGE: Final[str] = "catala"

# Conversión centralizada código ISO 639-1 -> idioma interno.
# El CLI acepta los códigos ISO (ca, es, en) y el resto del paquete
# trabaja siempre con los nombres internos. NO duplicar este mapa:
# usa siempre estas constantes.
LANGUAGE_CODES: Final[dict[str, str]] = {
    "ca": "catala",
    "es": "castellano",
    "en": "english",
}
# Conversión inversa (idioma interno -> ISO 639-1), usada para el
# atributo ``lang`` del HTML y para el nombre de los ficheros.
INTERNAL_LANGUAGE_CODES: Final[dict[str, str]] = {
    internal: code for code, internal in LANGUAGE_CODES.items()
}

# Alias de compatibilidad con la nomenclatura anterior del paquete.
LANGUAGE_CODES_INTERNAL: Final[dict[str, str]] = INTERNAL_LANGUAGE_CODES
DEFAULT_LANGUAGE_CODE: Final[str] = "ca"


def normalize_language(value: str) -> str:
    """Convierte un código ISO 639-1 (o nombre interno) al idioma interno.

    Es la única correspondencia de idiomas del proyecto: no duplicar
    esta conversión en otros módulos.
    """
    return LANGUAGE_CODES.get(value, value)


# ------------------------------------------------------------------
# Configuración externa: umbral de aprobado e identidad visual (.env)
# ------------------------------------------------------------------
PASS_MARK_ENV: Final[str] = "PASS_MARK"
DEFAULT_PASS_MARK: Final[float] = 50.0

# Logotipo del bloque de marca de la cabecera del informe.
LOGO_ESCOLA_ENV: Final[str] = "LOGO_ESCOLA"
DEFAULT_SCHOOL_LOGO_URL: Final[str] = "..\data\logo.png"

# Plantilla de la fotografía del alumno (formato original: 0 + IDALUMNE).
FOTO_ALUMNE_ENV: Final[str] = "FOTO_ALUMNE"
DEFAULT_STUDENT_PHOTO_URL_TEMPLATE: Final[str] = (
    "..\data\student_ia\{student_id}.jpg"
)


def _env_float(name: str, default: float) -> float:
    """Lee una variable de entorno como ``float``; si falta o no es
    numérica finita, devuelve el valor por defecto."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw.replace(",", "."))
    except ValueError:
        return default
    return value if math.isfinite(value) else default


# Nota mínima para aprobar. Una nota exactamente igual se considera
# aprobada. Proviene EXCLUSIVAMENTE del .env (``PASS_MARK``).
Pass_mark: Final[Any] = _env_float(PASS_MARK_ENV, DEFAULT_PASS_MARK)

SCHOOL_LOGO_URL: Final[str] = (
    os.getenv(LOGO_ESCOLA_ENV, "").strip() or DEFAULT_SCHOOL_LOGO_URL
)
STUDENT_PHOTO_URL_TEMPLATE: Final[str] = (
    os.getenv(FOTO_ALUMNE_ENV, "").strip() or DEFAULT_STUDENT_PHOTO_URL_TEMPLATE
)

# Nombre de la escuela en el pie del informe (no se traduce).
REPORT_SCHOOL_NAME: Final[str] = "Escola Comunica't"

# ------------------------------------------------------------------
# Reglas de validación
# ------------------------------------------------------------------
VALID_PRIORITIES: Final[frozenset[str]] = frozenset({"High", "Medium", "Low"})
MIN_ACTIVITIES: Final[int] = 2
MAX_ACTIVITIES: Final[int] = 4
SCORE_TOLERANCE: Final[float] = 0.01

# ------------------------------------------------------------------
# LLM / OpenRouter
# ------------------------------------------------------------------
OPENROUTER_BASE_URL: Final[str] = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY_ENV: Final[str] = "OPENROUTER_API_KEY"

# Nombre del modelo LLM: se lee de la variable de entorno MODEL_LLM
# (definida en el .env de la raíz del proyecto). Si no está definida,
# se mantiene el modelo actual como valor por defecto: no hay que
# tocar código Python para cambiar de modelo.
# Modelos alternativos probados anteriormente:
#   apodex/apodex-1.1-mini:free, liquid/lfm-2.5-2.6b:free,
#   nvidia/nemotron-3.5-lightning:free, poolside/laguna-xs-2.1:free,
#   nvidia/nemotron-3-ultra-550b-a55b:free
MODEL_LLM_ENV: Final[str] = "MODEL_LLM"
DEFAULT_LLM_MODEL: Final[str] = "nvidia/nemotron-3.5-super-vl:free"
LLM_MODEL: Final[str] = (
    os.getenv(MODEL_LLM_ENV, "").strip() or DEFAULT_LLM_MODEL
)
LLM_EXTRA_BODY: Final[dict[str, dict[str, bool]]] = {
    "reasoning": {"enabled": True}
}
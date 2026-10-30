"""Hoja de estilos del informe: CSS corporativo + estilos propios."""

from __future__ import annotations

from pathlib import Path

from student_report.config.settings import REPORT_CSS_ASSET, REPORT_CSS_FILENAME

__all__ = ["load_report_css", "build_stylesheet"]


def load_report_css(path: Path = REPORT_CSS_ASSET) -> str:
    """Devuelve los estilos adicionales del informe (``assets/report.css``)."""
    return path.read_text(encoding="utf-8")


def build_stylesheet(base_css_path: str | Path, output_dir: Path) -> Path:
    """Combina ``style.css`` con los estilos del informe en ``informe.css``.

    Raises:
        FileNotFoundError: si no existe la hoja de estilos corporativa.
    """
    source = Path(base_css_path)
    if not source.is_file():
        raise FileNotFoundError(
            f"No s'ha trobat la fulla d'estils: {source}. "
            "Desa style.css al directori del projecte o indica "
            "la ruta correcta amb el paràmetre ruta_css."
        )
    base_css = source.read_text(encoding="utf-8")
    target = output_dir / REPORT_CSS_FILENAME
    # Mismo separador que la versión v9 del script original.
    target.write_text(base_css + "\n\n" + load_report_css(), encoding="utf-8")
    return target
"""Generación de informes HTML."""

from student_report.reports.html_renderer import render_report_html, write_html_report
from student_report.reports.stylesheet import build_stylesheet, load_report_css

__all__ = [
    "build_stylesheet",
    "load_report_css",
    "render_report_html",
    "write_html_report",
]

"""Renderizado del informe pedagógico en HTML (versión v9).

Separa la *generación* del documento (:func:`render_report_html`, pura,
sin efectos secundarios) de su *escritura* a disco
(:func:`write_html_report`). Todos los textos dinámicos, incluidos los
que provienen del LLM, se escapan para evitar inyección de HTML.

Cambios v9 integrados:

- Cabecera con bloque de marca (logo + Comunica-T + School) y filas de
  información académica en tres columnas.
- Fotografía del alumno con borde amarillo (``--highlight-yellow``),
  el mismo color del borde de la tarjeta del resultado final.
- Tarjeta "Resultat final / Resultado final / Final result".
- Columna ``Pass/No pass`` en la tabla de competencias: barra
  horizontal con gradiente rojo→amarillo→verde, marcador de la nota
  real, marcador del umbral ``PASS_MARK`` del ``.env`` y etiqueta de estado
  (Pass en verde / No pass en rojo). Sin marcos amarillos extra.
- Puntos fuertes y aspectos a mejorar en UNA sola fila con número de
  celdas dinámico.
- Pie en dos bandas: identificación (blanco) y contacto (amarillo).
- ``--analisis-ia false``: la sección de análisis con IA no se genera.
- Atributo ``lang`` del HTML con el código ISO 639-1 y nombre de
  fichero con el código ISO.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from student_report.config.settings import (
    BASE_CSS_PATH,
    INTERNAL_LANGUAGE_CODES,
    OUTPUT_DIR,
    Pass_mark,
    REPORT_SCHOOL_NAME,
    SCHOOL_LOGO_URL,
    SKILLS_LOWER,
    STUDENT_PHOTO_URL_TEMPLATE,
)
from student_report.config.translations import get_ui_texts
from student_report.reports.stylesheet import build_stylesheet
from student_report.utils.html_utils import clamp_score, format_score
from student_report.utils.html_utils import escape_html as esc

__all__ = ["render_report_html", "write_html_report", "exam_state"]

# Prioridad del LLM -> (clave de traducción, clase CSS)
_PRIORITIES: dict[str, tuple[str, str]] = {
    "High": ("high", "priority-high"),
    "Medium": ("medium", "priority-medium"),
    "Low": ("low", "priority-low"),
}
_DEFAULT_PRIORITY: tuple[str, str] = ("medium", "priority-medium")

# Estados del examen: la nota exactamente igual al umbral es Pass.
_STATUS_PASS = "pass"
_STATUS_NO_PASS = "no-pass"
_STATUS_UNAVAILABLE = "unavailable"

# Escala académica de la barra Pass/No pass (puntuaciones 0-100).
_PASS_SCALE_MIN = 0.0
_PASS_SCALE_MAX = 100.0

# Enlaces del pie de contacto (datos reales de la escuela; no editar).
_CONTACT_LINKS: tuple[tuple[str, str], ...] = (
    (
        "https://www.google.com/maps/search/?api=1&query=Entença%2C%2089%2C%2008015%2C%20Barcelona",
        "📍 Entença, 89, 08015, Barcelona",
    ),
    ("tel:+34934262479", "☎ 934 262 479"),
    ("https://wa.me/34601302029", "💬 601 30 20 29"),
    ("mailto:info@comunicat.school", "✉ info@comunicat.school"),
    ("https://www.comunicat.school", "🌐 www.comunicat.school"),
)

SkillLabel = Callable[[str], str]


# ------------------------------------------------------------------
# Estado Pass / No pass
# ------------------------------------------------------------------

def exam_state(
    average: Any, pass_mark: Any
) -> str:
    """Clasifica el resultado: ``pass``, ``no-pass`` o ``unavailable``.

    Una nota exactamente igual al umbral se considera aprobada. Si falta
    la nota o el umbral (o no son numéricos finitos) devuelve
    ``unavailable``: no se inventa ningún valor.
    """
    try:
        average_num = float(average)
        average_valid = math.isfinite(average_num)
    except (TypeError, ValueError):
        average_valid = False

    try:
        pass_mark_num = float(pass_mark)
        pass_mark_valid = math.isfinite(pass_mark_num)
    except (TypeError, ValueError):
        pass_mark_valid = False

    if not average_valid or not pass_mark_valid:
        return _STATUS_UNAVAILABLE
    if average_num >= pass_mark_num:
        return _STATUS_PASS
    return _STATUS_NO_PASS


def _pass_position(value: float) -> float:
    """Posición percentual de ``value`` dentro de la escala académica."""
    span = _PASS_SCALE_MAX - _PASS_SCALE_MIN
    if span <= 0:
        return 0.0
    clamped = max(_PASS_SCALE_MIN, min(_PASS_SCALE_MAX, value))
    return ((clamped - _PASS_SCALE_MIN) / span) * 100.0


# ------------------------------------------------------------------
# Fragmentos HTML
# ------------------------------------------------------------------

def _skill_label_factory(t: Mapping[str, str]) -> SkillLabel:
    """Devuelve una función que traduce y escapa el nombre de una competencia."""

    def skill_label(skill: str) -> str:
        return esc(t.get(skill, skill.capitalize()))

    return skill_label


def _donut_chart(label: str, value: Any, css_class: str = "") -> str:
    """Gráfico circular de progreso 0-100 con CSS ``conic-gradient``."""
    score = clamp_score(value)
    angle = score * 3.6

    return f"""
        <div class="score-card {css_class}">
            <div
                class="donut-chart"
                role="img"
                aria-label="{esc(label)}: {format_score(score)}%"
                style="--score-angle: {angle:.2f}deg;"
            >
                <div class="donut-inner">
                    <span class="donut-value">
                        {format_score(score)}
                    </span>
                    <span class="donut-percent">%</span>
                </div>
            </div>
            <h3>{esc(label)}</h3>
        </div>
        """


def _summary_cards(
    t: Mapping[str, str], average: float, best: str, weakest: str,
    skill_label: SkillLabel,
) -> str:
    """Tarjetas de resumen: media, mejor competencia y a reforzar."""
    return f"""
    <div class="summary-grid">
        <article class="summary-card">
            <span class="summary-label">{esc(t["average"])}</span>
            <strong class="summary-number">{format_score(average)}%</strong>
        </article>

        <article class="summary-card summary-best">
            <span class="summary-label">{esc(t["best"])}</span>
            <strong class="summary-text">{skill_label(best)}</strong>
        </article>

        <article class="summary-card summary-weakest">
            <span class="summary-label">{esc(t["weakest"])}</span>
            <strong class="summary-text">{skill_label(weakest)}</strong>
        </article>
    </div>
    """


def _pass_bar_html(
    t: Mapping[str, str],
    average_original: Any,
    pass_mark: Any,
) -> str:
    """Barra horizontal Pass/No pass con marcadores dinámicos.

    Ambas posiciones (nota del alumno y umbral) se calculan sobre la
    misma escala académica 0-100; el umbral proviene de ``.env`` (``PASS_MARK``).
    """
    try:
        average_num = float(average_original)
        average_available = math.isfinite(average_num)
    except (TypeError, ValueError):
        average_available = False

    try:
        pass_mark_num = float(pass_mark)
        pass_mark_valid = math.isfinite(pass_mark_num)
    except (TypeError, ValueError):
        pass_mark_valid = False

    average = clamp_score(average_original)
    state = exam_state(average_original, pass_mark)
    if state == _STATUS_UNAVAILABLE:
        state_text = t["result_unavailable"]
    elif state == _STATUS_PASS:
        state_text = "Pass"
    else:
        state_text = "No pass"

    # Marcador del umbral de aprobado.
    pass_bar_marker = ""
    pass_mark_label = f"{t['pass_mark']}: {t['no_data']}"
    if pass_mark_valid:
        threshold_position = _pass_position(pass_mark_num)
        pass_bar_marker = (
            '<span class="pass-threshold-marker" '
            f'style="--marker-position: {threshold_position:.4f}%" '
            'aria-hidden="true"></span>'
        )
        pass_mark_label = f"{t['pass_mark']}: {format_score(pass_mark_num)}"

    # Marcador de la nota real del alumno.
    score_marker = ""
    if average_available:
        score_position = _pass_position(average)
        score_marker = (
            '<span class="pass-score-marker" '
            f'style="--marker-position: {score_position:.4f}%" '
            f'title="Resultat final: {format_score(average)}%" '
            f'aria-label="Resultat final: {format_score(average)}%">'
            f'<span class="pass-score-value">{format_score(average)}%</span>'
            '</span>'
        )

    return f"""
        <div class="pass-bar-component">
            <div class="pass-bar-horizontal-wrap">
                <div class="pass-bar-scale-labels">
                    <span>{format_score(_PASS_SCALE_MIN)}</span>
                    <span>{format_score(_PASS_SCALE_MAX)}</span>
                </div>
                <div class="pass-bar pass-bar-horizontal" role="img"
                     aria-label="Escala de resultats de {format_score(_PASS_SCALE_MIN)} a {format_score(_PASS_SCALE_MAX)}. {esc(pass_mark_label)}. {esc(state_text)}.">
                    {pass_bar_marker}
                    {score_marker}
                </div>
            </div>
            <div class="pass-bar-details">
                <div class="pass-mark-label">{esc(pass_mark_label)}</div>
                <div class="pass-result-label exam-status-{state}" role="status">
                    {esc(state_text)}
                </div>
            </div>
        </div>
    """


def _score_rows(
    scores: Mapping[str, Any], skill_label: SkillLabel, pass_bar: str
) -> str:
    """Filas ``<tr>`` de la tabla con la columna Pass/No pass (rowspan)."""
    skills = list(SKILLS_LOWER)
    rows: list[str] = []
    for index, skill in enumerate(skills):
        status_cell = (
            f'<td class="pass-status-cell" rowspan="{len(skills)}">{pass_bar}</td>'
            if index == 0
            else ""
        )
        rows.append(
            f"""
        <tr>
            <td>{skill_label(skill)}</td>
            <td class="score-cell">
                {format_score(scores.get(skill, 0))}%
            </td>
            {status_cell}
        </tr>
        """
        )
    return "".join(rows)


def _empty(message: str) -> str:
    """Mensaje para secciones sin contenido."""
    return f'<p class="empty-message">{esc(message)}</p>'


def _strengths_html(
    items: Sequence[Mapping[str, Any]], t: Mapping[str, str],
    skill_label: SkillLabel,
) -> str:
    """Tarjetas de puntos fuertes."""
    if not items:
        return _empty(t["no_strengths"])
    return "".join(
            f"""
            <article class="pedagogy-card strength-card">
                <div class="skill-badge">{skill_label(item.get("skill", ""))}</div>
                <div class="pedagogy-score">
                    {format_score(item.get("score", 0))}%
                </div>
                <p>{esc(item.get("observation", ""))}</p>
            </article>
            """
        for item in items
    )


def _improvements_html(
    items: Sequence[Mapping[str, Any]], t: Mapping[str, str],
    skill_label: SkillLabel,
) -> str:
    """Tarjetas de aspectos a mejorar con su prioridad traducida."""
    if not items:
        return _empty(t["no_improvements"])
    parts: list[str] = []
    for item in items:
        priority_key, priority_class = _PRIORITIES.get(
            item.get("priority", ""), _DEFAULT_PRIORITY
        )
        priority_label = t[priority_key]
        parts.append(
            f"""
            <article class="pedagogy-card improvement-card">
                <div class="improvement-header">
                    <h3>{skill_label(item.get("skill", ""))}</h3>
                    <span class="priority-badge {priority_class}">
                        {esc(t["priority"])}: {esc(priority_label)}
                    </span>
                </div>
                <div class="pedagogy-score">
                    {format_score(item.get("score", 0))}%
                </div>
                <p>{esc(item.get("observation", ""))}</p>
            </article>
            """
        )
    return "".join(parts)


def _activities_html(
    items: Sequence[Mapping[str, Any]], t: Mapping[str, str],
    skill_label: SkillLabel,
) -> str:
    """Tarjetas numeradas de actividades propuestas."""
    if not items:
        return _empty(t["no_activities"])
    parts: list[str] = []
    for index, activity in enumerate(items, start=1):
        parts.append(
            f"""
            <article class="activity-card">
                <div class="activity-number">{index}</div>
                <div class="activity-content">
                    <span class="skill-badge">
                        {skill_label(activity.get("skill", ""))}
                    </span>

                    <h3>{esc(activity.get("description", ""))}</h3>

                    <div class="activity-field">
                        <h4>{esc(t["procedure"])}</h4>
                        <p>{esc(activity.get("procedure", ""))}</p>
                    </div>

                    <div class="activity-objective">
                        <h4>{esc(t["objective"])}</h4>
                        <p>{esc(activity.get("learning_objective", ""))}</p>
                    </div>
                </div>
            </article>
            """
        )
    return "".join(parts)


def _ai_section_html(
    t: Mapping[str, str],
    strengths_html: str,
    improvements_html: str,
    skills_balance: str,
    activities_html: str,
    strengths_count: int,
    improvements_count: int,
) -> str:
    """Sección del análisis pedagógico generado por la IA (solo si hay IA).

    Puntos fuertes y aspectos a mejorar van en UNA sola fila: el número
    de columnas es dinámico (una celda por elemento del LLM).
    """
    return f"""
        <!-- ==================================================
             BLOC 3. INFORME PEDAGÒGIC GENERAT PER LA LLM
             ================================================== -->

        <section class="report-section">
            <div class="section-header">
                <h2>{esc(t["ai_label"])}</h2>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["strengths"])}</h3>
                <div class="pedagogy-grid strengths-grid" style="grid-template-columns: repeat({max(strengths_count, 1)}, minmax(0, 1fr));">
                    {strengths_html}
                </div>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["improvements"])}</h3>
                <div class="pedagogy-grid improvements-grid" style="grid-template-columns: repeat({max(improvements_count, 1)}, minmax(0, 1fr));">
                    {improvements_html}
                </div>
            </div>

            <div class="balance-card">
                <h3>{esc(t["balance"])}</h3>
                <p>{skills_balance}</p>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["activities"])}</h3>
                <div class="activities-list">
                    {activities_html}
                </div>
            </div>
        </section>
        """


# ------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------

def render_report_html(
    report: Mapping[str, Any],
    language: str,
    extra_info: Mapping[str, Any] | None = None,
    include_ai_analysis: bool = True,
) -> str:
    """Genera el documento HTML completo del informe (sin escribir a disco).

    Bloques: cabecera de la evaluación, resultados con gráficos,
    análisis pedagógico del LLM (si ``include_ai_analysis``) y
    comentario original del profesor.

    Args:
        report: JSON validado devuelto por el LLM. Con IA desactivada
            basta ``{"student_data": <perfil>}``.
        language: idioma interno (``catala``, ``castellano``, ``english``).
        extra_info: datos de cabecera (``student_name``, ``course``,
            ``teacher``, ``evaluation_description``, ``school_year``,
            ``teacher_comment``).
        include_ai_analysis: ``False`` omite la sección de análisis IA.

    Raises:
        ValueError: si el idioma no está soportado.
    """
    t = get_ui_texts(language)
    data = report.get("student_data", {}) or {}
    scores = data.get("skills", {}) or {}
    extra_info = extra_info or {}
    skill_label = _skill_label_factory(t)

    def extra(key: str) -> str:
        value = esc(extra_info.get(key))
        return value if value else esc(t["no_data"])

    student_id = esc(data["student_id"])
    evaluation_date = esc(data.get("evaluation_date", ""))
    try:
        formatted_evaluation_date = datetime.fromisoformat(
            str(data.get("evaluation_date"))
        ).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        formatted_evaluation_date = evaluation_date

    photo_url = STUDENT_PHOTO_URL_TEMPLATE.format(student_id=student_id)

    # El umbral de aprobado proviene EXCLUSIVAMENTE del .env (PASS_MARK).
    average_original = data.get("average")
    average = clamp_score(average_original)

    # La nota mínima prové exclusivament del .env (PASS_MARK).
    pass_bar = _pass_bar_html(t, average_original, Pass_mark)

    average_chart = _donut_chart(t["average"], average, "average-card")
    skill_charts = "".join(
        _donut_chart(skill_label(skill), scores.get(skill, 0))
        for skill in SKILLS_LOWER
    )
    summary_cards = _summary_cards(
        t, average, data.get("best_skill", ""), data.get("weakest_skill", ""),
        skill_label,
    )
    score_rows = _score_rows(scores, skill_label, pass_bar)

    strengths = list(report.get("strengths", []) or [])
    improvements = list(report.get("areas_to_improve", []) or [])
    strengths_html = _strengths_html(strengths, t, skill_label)
    improvements_html = _improvements_html(improvements, t, skill_label)
    skills_balance = esc(report.get("skills_balance", ""))
    activities_html = _activities_html(
        report.get("proposed_activities", []) or [], t, skill_label
    )
    teacher_comment = esc(extra_info.get("teacher_comment")) or esc(t["no_comment"])

    ai_section = ""
    if include_ai_analysis and report:
        ai_section = _ai_section_html(
            t,
            strengths_html,
            improvements_html,
            skills_balance,
            activities_html,
            len(strengths),
            len(improvements),
        )

    html_lang = INTERNAL_LANGUAGE_CODES.get(language, language)

    contact_links = "\n".join(
        f'                <a href="{href}" target="_blank" rel="noopener noreferrer">{label}</a>'
        if href.startswith("http")
        else f'                <a href="{href}">{label}</a>'
        for href, label in _CONTACT_LINKS
    )

    return f"""<!DOCTYPE html>
<html lang="{esc(html_lang)}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{esc(t["title"])} - {student_id}</title>

    <link rel="stylesheet" href="informe.css">
</head>

<body class="student-report">

    <div class="report-toolbar no-print">
        <button class="btn btn-primary" onclick="window.print()">
            {esc(t["print"])}
        </button>
    </div>

    <main class="container report-container">

        <!-- ==================================================
             BLOC 1. CAPÇALERA DE L'AVALUACIÓ
             ================================================== -->

        <header class="report-header">
            <div class="header-visual-row">
                <div class="report-brand">
                    <img src="{esc(SCHOOL_LOGO_URL)}"
                         alt="Logo de l'escola"
                         class="school-logo">
                    <span class="brand-text">Comunica-T</span>
                    <span class="brand-subtext">School</span>
                </div>
                <div class="report-heading">
                    <h1>{esc(t["title"])}</h1>
                    <p class="report-subtitle">{esc(t["subtitle"])}</p>
                </div>
                <div class="student-photo-container">
                    <img src="{esc(photo_url)}" alt="{esc(t["student"])}" class="student-photo"
                         onerror="this.style.display='none'">
                </div>
            </div>

            <div class="header-info-row academic-info-row">
                <div class="header-info-item">
                    <span>{esc(t["school_year"])}</span>
                    <strong>{extra("school_year")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["course"])}</span>
                    <strong>{extra("course")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["student"])}</span>
                    <strong>{extra("student_name")}</strong>
                </div>
            </div>

            <div class="header-info-row evaluation-info-row">
                <div class="header-info-item">
                    <span>{esc(t["teacher"])}</span>
                    <strong>{extra("teacher")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["evaluation"])}</span>
                    <strong>{extra("evaluation_description")} ({formatted_evaluation_date})</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["student_id"])}</span>
                    <strong>{student_id}</strong>
                </div>
            </div>
        </header>


        <!-- ==================================================
             BLOC 2. RESULTATS ACADÈMICS
             ================================================== -->

        <section class="report-section">
            <div class="section-header">
                <h2>{esc(t["results"])}</h2>
            </div>

            {summary_cards}

            <div class="scores-layout">

                <div class="average-chart-panel">
                    <h3>{esc(t["result_final"])}</h3>
                    {average_chart}
                </div>

                <div class="skills-panel">
                    <h3>{esc(t["skills"])}</h3>

                    <div class="scores-grid">
                        {skill_charts}
                    </div>
                </div>

            </div>

            <div class="scores-table-container">
                <table class="scores-table">
                    <thead>
                        <tr>
                            <th>{esc(t["skills"])}</th>
                            <th>{esc(t["score"])}</th>
                            <th class="pass-status-heading">Pass/No pass</th>
                        </tr>
                    </thead>
                    <tbody>
                        {score_rows}
                    </tbody>
                </table>
            </div>
        </section>


        {ai_section}

        <!-- ==================================================
             BLOC 4. COMENTARI DEL PROFESSOR
             ================================================== -->

        <section class="report-section teacher-report-section">
            <div class="section-header">
                <h2>{esc(t["teacher_comment"])}</h2>
            </div>

            <div class="teacher-comment-card">
                <div class="teacher-comment-label">
                    {esc(t["teacher_label"])}
                </div>

                <p class="teacher-comment-intro">
                    {esc(t["teacher_comment_intro"])}
                </p>

                <div class="teacher-comment-text">{teacher_comment}</div>

                <div class="teacher-signature">
                    {esc(t["teacher"])}:
                    <strong>{extra("teacher")}</strong>
                </div>
            </div>
        </section>


        <footer class="report-footer">
            <p class="report-footer-caption">{esc(t["footer"])} <span class="footer-separator">|</span> <span class="footer-school-name">{esc(REPORT_SCHOOL_NAME)}</span></p>
            <nav class="contact-footer" aria-label="Contacte de l'escola">
{contact_links}
            </nav>
        </footer>

    </main>
</body>
</html>
"""


def write_html_report(
    report: Mapping[str, Any],
    language: str,
    extra_info: Mapping[str, Any] | None = None,
    output_dir: str | Path = OUTPUT_DIR,
    base_css_path: str | Path = BASE_CSS_PATH,
    include_ai_analysis: bool = True,
) -> Path:
    """Genera el HTML, escribe ``informe.css`` y guarda el informe.

    Nombre del fichero: ``informe_<id>_<fecha>_<ISO 639-1>.html``.

    Returns:
        Ruta del HTML generado.

    Raises:
        ValueError: idioma no soportado.
        FileNotFoundError: no existe la hoja de estilos corporativa.
    """
    document = render_report_html(
        report, language, extra_info, include_ai_analysis
    )

    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    build_stylesheet(base_css_path, folder)

    data = report["student_data"]
    language_code = INTERNAL_LANGUAGE_CODES.get(language, language)
    filename = (
        f"informe_{esc(data['student_id'])}_"
        f"{esc(data['evaluation_date'])}_{language_code}.html"
    )
    html_path = folder / filename
    html_path.write_text(document, encoding="utf-8")
    return html_path
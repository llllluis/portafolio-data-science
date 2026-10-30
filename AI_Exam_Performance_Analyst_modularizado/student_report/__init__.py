"""student_report — análisis de resultados de inglés e informes con LLM.

Paquete que procesa las notas de las cinco competencias (Grammar,
Listening, Reading, Speaking y Writing) de un alumno, solicita una
interpretación pedagógica a un LLM vía OpenRouter, valida la respuesta
y genera un informe HTML en catalán, castellano o inglés.

API pública de alto nivel::

    from student_report import PipelineConfig, run_pipeline

    result = run_pipeline(PipelineConfig(student_id=1690,
                                         evaluation_date="2026-06-20",
                                         language="castellano"))
    print(result.html_path)
"""

from student_report.services.pipeline import (
    PipelineConfig,
    PipelineResult,
    run_pipeline,
)

__all__ = ["PipelineConfig", "PipelineResult", "run_pipeline"]
__version__ = "1.0.0"

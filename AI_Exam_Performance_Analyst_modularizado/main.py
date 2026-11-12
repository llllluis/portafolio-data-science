"""Punto de entrada del proyecto.

Uso por consola::

    python main.py --idalumne 1701 --idevaluacio 101 --idcurs 7 \
        --language es --analisis-ia true

La fecha de la evaluación no se indica: se lee del CSV de resultados
(columna ``DATA``) usando la combinación de los tres identificadores.
"""

from student_report.cli import main

if __name__ == "__main__":
    main()
# Análisis de influencia de materias en nota final de inglés

## Contexto
Dataset filtrado de alumnado de inglés en cursos extensivos. Se excluyen variables demográficas (99% Barcelona) y características del curso porque todos son extensivos. La unidad es alumno-curso-evaluación-materia.

## Objetivo
Cuantificar el peso relativo de Reading, Grammar, Writing, Listening, Speaking en TOTAL.

## Tecnologías
- Pandas (limpieza y agregación)
- Seaborn/Matplotlib (matriz de correlación, pairplots)
- Scikit-learn (regresión lineal, R², coeficientes)

## Estructura del proyecto
- `analisis.ipynb` o `script.py` - código principal
- `datos/` - contiene dataset anonimizado (si se puede compartir)
- `outputs/` - gráficos y tablas de resultados

## Resultados principales
- [Inserta aquí: la materia con mayor coeficiente, R² ajustado, conclusión ejecutiva]

## Cómo ejecutar
```bash
pip install pandas seaborn matplotlib scikit-learn
python analisis.py
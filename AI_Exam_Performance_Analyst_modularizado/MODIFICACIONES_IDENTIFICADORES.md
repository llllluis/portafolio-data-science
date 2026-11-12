# Modificación: identificación por IDALUMNE + IDEVALUACIO + IDCURS

Cambio funcional y de configuración sobre el proyecto existente. No se ha
reescrito ni refactorizado nada fuera del alcance: cálculos de las cinco
habilidades, ponderaciones, media, mejor/peor, criterios pedagógicos,
prompts, esquema JSON, validación de la IA y diseño del informe HTML
quedan intactos.

## 1. Resumen

- `--DATA` desaparece del CLI y deja de ser criterio de búsqueda.
- Nuevos argumentos obligatorios: `--idalumne`, `--idevaluacio`, `--idcurs`.
- La fecha de la evaluación se lee del CSV de resultados (columna `DATA`).
- Los dos CSV se configuran con `RESULTS_CSV_PATH` y `EXTRA_INFO_CSV_PATH`
  en `.env`; las rutas relativas se resuelven contra la raíz del proyecto.
- Nombre del informe: `informe_<alumno>_<fecha>_<evaluación>_<curso>_<idioma>.html`
  para que dos cursos del mismo alumno y fecha no se sobrescriban.

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `student_report/config/settings.py` | `PROJECT_ROOT`, rutas de los CSV desde `.env`, `resolve_project_path()`, `get_csv_path()`, `REQUIRED_RESULTS_COLUMNS` |
| `student_report/core/exceptions.py` | Nuevas `MultipleRecordsFoundError` y `DataValidationError` |
| `student_report/core/data_loader.py` | Filtro por los tres IDs, validación de columnas/habilidades/fecha, detección de duplicados, fecha obtenida del CSV |
| `student_report/core/extra_info.py` | `build_report_context()` filtra por `IDALUMNE + IDEVALUACIO + IDCURS`; mensajes de error en castellano |
| `student_report/core/__init__.py` | Exporta los nuevos símbolos |
| `student_report/services/pipeline.py` | `PipelineConfig` sin `evaluation_date`, con `evaluation_id` y `course_id`; validaciones y fecha desde el CSV |
| `student_report/cli.py` | `--idalumne`, `--idevaluacio`, `--idcurs`; `parse_course_id`; salida limpia ante errores controlados |
| `student_report/reports/html_renderer.py` | `save_rendered_html()`/`write_html_report()` aceptan `evaluation_id` y `course_id` para el nombre del fichero |
| `student_report/utils/io.py` | `ensure_source_csvs()`: valida ambos CSV al arrancar |
| `student_report/__init__.py`, `__main__.py`, `main.py`, `README.md` | Documentación y ejemplos actualizados |
| `.env.example` | Nuevas variables `RESULTS_CSV_PATH` y `EXTRA_INFO_CSV_PATH` |
| `tests/test_report.py` | Adaptado a la nueva clave |
| `tests/test_identifiers.py` | **Nuevo**: cubre las 7 pruebas pedidas |

`student_report/core/analysis.py` NO se ha tocado: sigue recibiendo la
fecha ya resuelta y los cálculos no cambian.

## 3. Comandos

```bash
python main.py --idalumne 1701 --idevaluacio 101 --idcurs 7 --language es --analisis-ia true
python main.py --idalumne 1701 --idevaluacio 101 --idcurs 8 --language ca --analisis-ia false
python -m student_report --idalumne 1701 --idevaluacio 101 --idcurs 7
```

`.env`:

```dotenv
RESULTS_CSV_PATH=data/NOTA_PARCIAL_PONDERADA_ALUMN.csv
EXTRA_INFO_CSV_PATH=data/INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv
```

## 4. Validaciones añadidas

- Combinación inexistente → `NoRecordsFoundError` con los tres IDs.
- `MATERIA` repetida en la combinación → `MultipleRecordsFoundError`
  (las 5 filas normales, una por habilidad, siguen siendo válidas).
- Falta alguna de las cinco habilidades → `DataValidationError`.
- `DATA` vacía, inválida o con fechas distintas dentro de la combinación
  → `DataValidationError`.
- Columnas obligatorias ausentes en cualquiera de los dos CSV → error claro.
- Duplicados de `IDALUMNE+IDEVALUACIO+IDCURS` en el CSV complementario →
  `ExtraInfoError` (comportamiento previo, mensaje en castellano).
- Rutas inexistentes o mal configuradas → `FileNotFoundError` indicando la
  variable de entorno y la ruta resuelta.

Nunca se elige un registro arbitrariamente cuando hay duplicados.

## 5. Pruebas

`python -m pytest tests -q` → **50 passed**.

| Prueba | Resultado |
|---|---|
| 1. Combinación válida | `Files trobades: 5`, fecha `2026-06-20` leída del CSV, informe generado |
| 2. Mismo alumno y fecha, curso 7 y 8 | Notas distintas, `informe_..._101_7_es.html` y `..._101_8_es.html`, ambos conservados |
| 3. Mismo alumno y curso, evaluaciones 101 y 102 | Fechas y notas distintas, ficheros distintos |
| 4. Combinación inexistente | Error controlado con los tres IDs, `rc=1` |
| 5. Duplicado de `MATERIA` | Error controlado indicando `GRAMMAR`, `rc=1` |
| 6. IA desactivada / activada | Sin LLM: `report` solo con `student_data`. Con LLM (mock): JSON completo y validado. Sin ficheros `.json` |
| 7. Rutas de CSV desde `.env` | Ejecución real con CSV en `/tmp/e2e/alt`; también probado con `importlib.reload(settings)` |

## 6. Riesgos y aspectos a comprobar

1. **Ruptura de API interna**: `PipelineConfig` ya no acepta `evaluation_date`.
   Cualquier script propio que lo construya debe pasar `evaluation_id` y
   `course_id`.
2. **Nombre de fichero**: cambia el patrón. Si algún proceso recoge
   `informe_<alumno>_<fecha>_<idioma>.html`, hay que actualizar el patrón.
3. **`IDCURS`**: se acepta numérico o alfanumérico. La comparación se hace
   normalizada como texto, así que `7`, `7.0` y `"7"` son equivalentes.
4. **`DATA` mixta** dentro de una misma combinación ahora es un error (antes
   el filtro por fecha lo ocultaba). Es intencionado.
5. **`OUTPUT_DIR` y `BASE_CSS_PATH` siguen siendo relativos al directorio de
   trabajo** (comportamiento original). Los CSV ya no dependen del CWD, pero
   conviene ejecutar desde la raíz del proyecto.
6. **Mensajes**: toda la salida de consola, los errores y el `--help`
   están unificados en castellano (incluidos los mensajes internos de
   argparse: argumentos obligatorios, argumentos no reconocidos, opciones
   y valores no válidos). Los textos del informe HTML NO cambian: siguen
   traduciéndose a `ca` / `es` / `en` según `--language`.
7. `python-dotenv` debe estar instalado (`requirements.txt` lo incluye); si no
   está, el `.env` se ignora silenciosamente y se usan los valores por defecto.

# AI Exam Performance Analyst — versión modularizada (integración v9)

Informe HTML de rendimiento académico de inglés con análisis pedagógico
asistido por LLM (OpenRouter), en català, castellano o inglés.

## Estructura

```
english_report/
├── main.py                     # Punto de entrada (python main.py ...)
├── style.css                   # Base corporativa (reconstruida; usa la tuya si la tienes)
├── requirements.txt
├── data/                       # CSV de ejemplo con datos ficticios
│   ├── NOTA_PARCIAL_PONDERADA_ALUMN.csv
│   └── INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv
├── reports/                    # Informes HTML generados (informe_<id>_<fecha>_<ca|es|en>.html)
├── tests/
│   ├── test_model_config.py
│   └── test_report.py          # Pruebas con LLM simulado (sin llamadas reales)
└── student_report/
    ├── cli.py                  # Argumentos: --idalumne --data --language --analisis-ia
    ├── config/                 # settings.py (config + idiomas), prompts.py, translations.py
    ├── core/                   # data_loader, analysis, extra_info, validation, exceptions
    ├── llm/                    # client (OpenRouter), prompt_builder
    ├── reports/                # html_renderer, stylesheet, assets/report.css
    ├── services/               # pipeline (flujo completo)
    └── utils/                  # io, ids, html_utils
```

## Ejecución

```bash
pip install -r requirements.txt

# Antes, crea .env a partir de .env.example y configura tu clave API privada.
# Con análisis IA (por defecto true; requiere OPENROUTER_API_KEY)
python main.py --idalumne 1701 --data 2026-06-20 --language ca --analisis-ia true

# Sin análisis IA (no se llama al LLM; el informe se genera igual)
python main.py --idalumne 1701 --data 2026-06-20 --language es --analisis-ia false
```

- `--language`: código ISO 639-1 (`ca`, `es`, `en`). Se aceptan también
  `catala`, `castellano`, `english` por compatibilidad.
- `--analisis-ia`: `true` (por defecto) | `false`.
- El nombre del fichero usa el código ISO: `informe_1701_2026-06-20_es.html`.
- Los CSV incluidos contienen datos ficticios. Sustitúyelos por tus propios datos en un entorno privado; no publiques información personal de estudiantes.

## Configuración mediante `.env`

**El antiguo `config.py` desaparece**: toda la configuración editable
vive ahora en el fichero `.env` de la raíz del proyecto (cópialo desde
`.env.example`), **sin modificar código Python**:

```dotenv
# Modelo LLM (OpenRouter)
MODEL_LLM=nvidia/nemotron-3.5-super-vl:free
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

# Académico: umbral de aprobado (una nota igual se considera aprobada).
# Toda la columna Pass/No pass lo lee de aquí; no hay umbrales fijos en HTML/CSS.
PASS_MARK=50.0

# Recursos visuales propios (rutas de ejemplo)
LOGO_ESCOLA=data/logo.png
FOTO_ALUMNE=data/student_ia/{student_id}.jpg
```

- El paquete carga `.env` al arrancar con `python-dotenv` (incluido en
  `requirements.txt`); las variables ya presentes en el entorno real
  tienen prioridad sobre el fichero.
- Valores por defecto si falta una variable: modelo
  `nvidia/nemotron-3.5-super-vl:free`, `PASS_MARK` `50.0`, logo y foto
  de Comunica-T.
- Si `PASS_MARK` no es un número válido, se usa el valor por defecto.
- La clave API solo es necesaria con `--analisis-ia true`; con
  `--analisis-ia false` no se lee ningún modelo ni clave.

## Resumen de cambios integrados (v9 → modular)

1. **CLI**: `--analisis-ia true|false` (por defecto `true`) y `--language`
   con códigos ISO 639-1; conversión centralizada en
   `settings.normalize_language` (sin duplicar mapas).
   `logo_escola` y `foto_alumne`; `settings.py` lo carga con valores
   por defecto.
3. **JSON solo en memoria**: la respuesta del LLM ya no se guarda en
   disco (sin `informes_json/` ni `.json`); la validación estructural y
   pedagógica se mantiene íntegra.
4. **Cabecera**: bloque de marca (logo + `Comunica-T` + `School`),
   filas de información académica en 3 columnas y fotografía con borde
   `--highlight-yellow` (mismo color que la tarjeta del resultado final).
5. **Tarjeta Resultat final**: título localizado, borde amarillo y gráfico
   circular en azul corporativo.
6. **Columna `Pass/No pass`** en la tabla de competencias: barra
   horizontal rojo→amarillo→verde con marcador de la nota real y del
   umbral (`config.Pass_mark`), etiqueta localizada del umbral y estado
   `Pass` (verde) / `No pass` (rojo) / "no disponible". Sin marco amarillo
   alrededor de la columna (requisito explícito).
7. **Puntos fuertes y aspectos a mejorar**: una sola fila con número de
   celdas dinámico (`repeat(N, minmax(0, 1fr))`), sin desbordes.
8. **Pie en dos bandas**: identificación (blanco, `| Escola Comunica't`)
   y contacto (amarillo) con enlaces reales (Google Maps, `tel:`,
   WhatsApp, `mailto:`, web).
9. **Impresión A4 horizontal** (landscape, 10 mm) con reglas de salto
   de página para tarjetas, tabla y pie.

## Pruebas ejecutadas

`python -m pytest tests -q` (LLM simulado, sin llamadas reales):

- CLI: `--language` ISO + compatibilidad, `--analisis-ia` `true`/`false`
  (por defecto `true`), valores inválidos rechazados.
  inferior → `No pass`; superior → `Pass`; sin nota/umbral → estado
  "no disponible" sin inventar valores.
- Tres idiomas: textos localizados, `lang` correcto y fichero con código ISO.
- `--analisis-ia false`: sin llamada al LLM y sin sección de IA; el HTML
  se genera con los resultados académicos.
- `--analisis-ia true` (mock): JSON validado (estructura y coherencia
  pedagógica) y renderizado completo.
- No se crea ningún fichero `.json` en disco.
- Filas dinámicas (3 fortalezas / 2 mejoras) y estados vacíos localizados.
- Bloque de marca, borde amarillo compartido y sin contorno en la columna.

## Limitaciones

- **No se han llamado al LLM real** (no hay clave API en este entorno);
  la integración con OpenRouter se mantiene sin cambios y se ha probado
  con un mock.
- **No se ha verificado la impresión real ni navegadores**: el CSS de
  impresión A4 horizontal se ha integrado tal cual de la v9.
- `style.css` es una **reconstrucción** con los tokens que consume el
  informe; si conservas tu `style.css` corporativo original, úsalo.
- Los CSV de `data/` incluidos son **ficticios** y se utilizan únicamente como datos de demostración. No se incluyen fotografías ni informes de alumnos.

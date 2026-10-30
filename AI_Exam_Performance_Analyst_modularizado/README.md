# AI Exam Performance Analyst — Versión modularizada

> Aplicación en Python que analiza los resultados parciales de un examen de inglés y genera un informe HTML personalizado del rendimiento académico, con interpretación pedagógica asistida por un modelo de lenguaje (LLM) mediante OpenRouter. Los informes pueden generarse en catalán, castellano o inglés.

---

## 📌 Descripción

El proyecto procesa las cinco competencias del examen —Grammar, Listening, Reading, Speaking y Writing—, analiza los resultados individuales, identifica fortalezas y áreas de mejora y propone actividades de aprendizaje.

La aplicación realiza los cálculos académicos y prepara el perfil del alumno. El LLM se utiliza para elaborar la interpretación pedagógica y las propuestas de actividades. La respuesta del modelo se valida antes de incorporarse al informe.

Esta versión organiza el código en módulos con responsabilidades diferenciadas, en lugar de concentrar el flujo completo en un único archivo. Se desarrolló a partir de la versión monolítica del proyecto, utilizando una herramienta de IA como asistente para reorganizar la aplicación y facilitar su mantenimiento y evolución.

> **Versión monolítica:** [https://github.com/llllluis/portafolio-data-science/tree/main/AI_Exam_Performance_Analyst_monolitico]

---

## ✨ Funcionalidades

1. Lectura y filtrado de datos desde archivos CSV.
2. Cálculo y análisis de resultados de las cinco competencias.
3. Preparación del perfil individual del alumno.
4. Integración con un modelo LLM mediante OpenRouter.
5. Validación estructural y pedagógica de la respuesta JSON generada por el modelo.
6. Generación de informes HTML en catalán, castellano o inglés.
7. Ejecución con o sin análisis mediante IA, utilizando el parámetro `--analisis-ia`.
8. Configuración del modelo, la nota mínima para aprobar y los recursos visuales mediante variables de entorno.
9. Pruebas automatizadas con el LLM simulado, sin realizar llamadas reales a la API.

> Las calificaciones y los cálculos académicos los realiza la aplicación; el LLM se utiliza para generar la interpretación pedagógica y las propuestas de actividades.

---

## 🗂️ Estructura del proyecto

```text
english_report/
├── main.py
├── style.css
├── requirements.txt
├── .env.example
├── data/
│   ├── NOTA_PARCIAL_PONDERADA_ALUMN.csv
│   └── INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv
├── reports/
├── tests/
│   ├── test_model_config.py
│   └── test_report.py
└── student_report/
    ├── cli.py
    ├── config/
    │   ├── settings.py
    │   ├── prompts.py
    │   └── translations.py
    ├── core/
    ├── llm/
    ├── reports/
    ├── services/
    └── utils/
```

Los módulos se agrupan por responsabilidad:

| Módulo | Responsabilidad |
|---|---|
| `config` | configuración de la aplicación, prompts e idiomas. |
| `core` | carga de datos, análisis, información adicional, validación y excepciones. |
| `llm` | cliente de OpenRouter y construcción del prompt. |
| `reports` | generación del informe HTML y recursos de estilos. |
| `services` | coordinación del flujo completo de procesamiento. |
| `utils` | funciones auxiliares para entrada/salida, identificadores y HTML. |
| `tests` | pruebas automatizadas de configuración y generación de informes. |

---

## 🛠️ Tecnologías

- Python
- Pandas
- CSV y JSON
- API de OpenRouter
- HTML y CSS
- `python-dotenv`
- `pytest`

---

## ⚙️ Configuración

1. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Crea un archivo `.env` a partir de `.env.example`.
3. Introduce tu clave privada de OpenRouter en `OPENROUTER_API_KEY`.
4. Si lo deseas, cambia `MODEL_LLM` para seleccionar otro modelo disponible en OpenRouter.
5. Ajusta `PASS_MARK`, `LOGO_ESCOLA` y `FOTO_ALUMNE` según tus necesidades.

**Ejemplo de configuración:**

```dotenv
# Modelo LLM (OpenRouter)
MODEL_LLM=nvidia/nemotron-3.5-super-vl:free
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

# Nota mínima para aprobar
PASS_MARK=50.0

# Recursos visuales
LOGO_ESCOLA=data/logo.png
FOTO_ALUMNE=data/student_ia/{student_id}.jpg
```

La configuración editable se centraliza en `.env`; no es necesario modificar el código Python para cambiar estos valores. El paquete carga el archivo mediante `python-dotenv`. Las variables definidas en el entorno tienen prioridad sobre las del archivo `.env`.

**Valores por defecto si falta una variable:**

- Modelo: `nvidia/nemotron-3.5-super-vl:free`.
- Nota mínima para aprobar: `50.0`.
- Logotipo y fotografía: recursos predeterminados de Comunica-T.

La clave API solo es necesaria cuando se ejecuta el análisis con IA. Con `--analisis-ia false` no se realiza ninguna llamada al LLM.

> 🔒 **No publiques el archivo `.env` ni incluyas claves API en GitHub.** El repositorio debe contener únicamente `.env.example` con valores de ejemplo.

---

## ▶️ Ejecución

**Con análisis de IA** (requiere una clave válida de OpenRouter):

```bash
python main.py --idalumne 1701 --data 2026-06-20 --language es --analisis-ia true
```

**Sin análisis de IA:**

```bash
python main.py --idalumne 1701 --data 2026-06-20 --language es --analisis-ia false
```

Idiomas disponibles: `ca` (catalán), `es` (castellano) y `en` (inglés). También se aceptan `catala`, `castellano` y `english` por compatibilidad.

El parámetro `--analisis-ia` acepta `true` o `false` y, si se omite, su valor predeterminado es `true`. Los informes HTML generados se guardan en `reports/` con el código ISO del idioma en el nombre del archivo, por ejemplo: `informe_1701_2026-06-20_es.html`.

La respuesta JSON del LLM se mantiene en memoria y no se guarda como archivo independiente.

---

## 🧪 Pruebas

Las pruebas se ejecutan con:

```bash
python -m pytest tests -q
```

La batería de pruebas utiliza un LLM simulado, por lo que no necesita realizar llamadas reales a OpenRouter. Comprueba, entre otros aspectos:

- Argumentos de la CLI, idiomas admitidos y valores de `--analisis-ia`.
- Configuración del modelo y de la nota mínima para aprobar.
- Generación de informes en los tres idiomas.
- Ejecución sin IA y ausencia de llamadas al LLM.
- Validación y renderizado de la respuesta simulada del LLM.
- Estados `Pass` y `No pass`, y casos sin nota o umbral disponible.
- Ausencia de archivos JSON generados en disco.
- Renderizado de fortalezas, aspectos a mejorar y elementos visuales del informe.

---

## ⚠️ Limitaciones

- No se realizan llamadas al LLM real durante las pruebas automatizadas; la integración con OpenRouter se comprueba mediante un mock.
- La impresión real y el comportamiento en distintos navegadores no se han verificado exhaustivamente. El CSS de impresión A4 horizontal está integrado en el proyecto.
- `style.css` es una reconstrucción de los estilos corporativos a partir de los elementos utilizados por el informe. Puede sustituirse por la hoja de estilos corporativa original si se dispone de ella.
- Los CSV incluidos en el repositorio son datos ficticios de demostración. No publiques información personal de estudiantes ni fotografías reales.

---

## 📊 Estado y alcance

La versión modularizada incluye el análisis de resultados, la validación de la respuesta del LLM, la interpretación pedagógica y la generación de informes HTML. La automatización para generar y enviar informes a todos los alumnos queda fuera del alcance de este proyecto y se plantea como un proyecto independiente.

---

## 🧠 Aprendizajes

Este proyecto permite estudiar cómo evoluciona una aplicación basada en datos e IA desde una estructura monolítica hacia una arquitectura modular. La separación por responsabilidades facilita localizar componentes, mantener el código y desarrollar pruebas específicas, aunque también requiere gestionar imports y dependencias entre módulos.

La IA se ha utilizado como asistente de desarrollo para reorganizar el proyecto. El objetivo ha sido revisar y comprender la estructura resultante, manteniendo la lógica funcional de la aplicación.
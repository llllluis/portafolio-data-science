# AI Exam Performance Analyst — Versión monolítica

> Aplicación en Python que analiza los resultados parciales de un examen de inglés y utiliza un modelo de lenguaje (LLM) para generar un informe personalizado del rendimiento académico. Procesa Grammar, Listening, Reading, Speaking y Writing, identifica fortalezas y áreas de mejora y propone actividades de aprendizaje. El informe se genera en HTML y puede redactarse en catalán, castellano o inglés.

---

## 📌 Descripción

Aplicación en Python que analiza los resultados parciales de un examen de inglés y utiliza un modelo de lenguaje (LLM) para generar un informe personalizado del rendimiento académico. Procesa Grammar, Listening, Reading, Speaking y Writing, identifica fortalezas y áreas de mejora y propone actividades de aprendizaje. El informe se genera en HTML y puede redactarse en catalán, castellano o inglés.

---

## 🎯 Objetivo de aprendizaje

Esta versión se ha desarrollado intencionadamente con una estructura monolítica: gran parte del proceso está reunido en un único archivo Python. Es una práctica de aprendizaje para construir la aplicación paso a paso y comprender cómo se conectan el análisis de datos, la llamada al LLM, la validación de la respuesta y la generación del informe. La prioridad inicial era entender los conceptos y el flujo completo antes de trabajar con una arquitectura más compleja.

Después de completar esta versión, se utilizó una herramienta de IA como asistente para transformar el proyecto en una versión modularizada. La comparación entre ambas permite estudiar las ventajas y los inconvenientes de cada estructura.

> **Versión modularizada:** _[https://github.com/llllluis/portafolio-data-science/tree/main/AI_Exam_Performance_Analyst_modularizado]._

---

## ✨ Funcionalidades

1. Lectura y filtrado de datos desde archivos CSV.
2. Cálculo y análisis de resultados de las cinco competencias.
3. Preparación del perfil individual del alumno.
4. Integración con un modelo LLM mediante OpenRouter.
5. Validación de la estructura JSON generada por el modelo.
6. Revisión de coherencia pedagógica.
7. Generación de un informe HTML multilingüe.

> Las calificaciones y los cálculos académicos los realiza la aplicación; el LLM se utiliza para generar la interpretación pedagógica y las propuestas de actividades.

---

## 🛠️ Tecnologías

- Python y Pandas
- CSV y JSON
- API de OpenRouter
- HTML y CSS
- Variables de entorno con `python-dotenv`

---

## ⚖️ Versión monolítica y versión modularizada

| Aspecto | Monolítica | Modularizada |
|---|---|---|
| **Aprendizaje inicial** | Permite seguir el flujo en un solo archivo. | Ayuda a aprender separación de responsabilidades. |
| **Estructura** | Más sencilla de iniciar y recorrer en un proyecto pequeño. | Distribuye el código en módulos con funciones específicas. |
| **Mantenimiento** | Puede resultar más difícil cuando el archivo crece. | Puede facilitar los cambios si los módulos están bien definidos. |
| **Reutilización** | Puede requerir extraer funciones para reutilizarlas. | Facilita reutilizar componentes independientes. |
| **Complejidad** | Menos archivos y menos navegación entre módulos. | Requiere gestionar imports y dependencias entre módulos. |
| **Depuración** | El flujo está concentrado, aunque el archivo puede crecer mucho. | Los errores pueden aislarse por módulo, pero hay que seguir las llamadas entre ellos. |

> Ninguna estructura es siempre mejor. La versión monolítica responde al objetivo de aprender y entender el proceso completo; la modularizada permite explorar una organización más mantenible cuando el proyecto crece.

---

## ⚙️ Configuración

1. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Copia `.env.example` y crea un archivo local llamado `.env`.
3. Introduce tu clave de OpenRouter en `MODEL_API_KEY`.
4. Ajusta `MODEL_LLM` si quieres utilizar otro modelo disponible en OpenRouter. El valor de ejemplo es `nvidia/nemotron-3.5-super-vl:free`.
5. Revisa `FOTO_ALUMNE`, `LOGO_ESCOLA` y `PASS_MARK` si necesitas cambiar la URL de la fotografía, el logotipo o la nota mínima para aprobar.

> 🔒 **No publiques el archivo `.env` ni incluyas claves API en GitHub.** `.gitignore` excluye este archivo del control de versiones.

---

## ▶️ Ejecución

**Con análisis de IA** (requiere una clave válida de OpenRouter):

```bash
python analyze_student_profile.py --idalumne 1701 --data 2026-06-20 --language es --analisis-ia true
```

**Sin análisis de IA:**

```bash
python analyze_student_profile.py --idalumne 1701 --data 2026-06-20 --language es --analisis-ia false
```

> Idiomas disponibles: `ca` (catalán), `es` (castellano) y `en` (inglés). Los informes HTML se guardan en `reports/`. La respuesta JSON del LLM se conserva en memoria y no se guarda como archivo JSON.

---

## 📊 Estado y alcance

La versión incluye análisis de resultados, validación de la respuesta del LLM, interpretación pedagógica y generación de informes HTML. La automatización para generar y enviar informes a todos los alumnos queda fuera del alcance de este proyecto y se plantea como un proyecto independiente.

---

## 🧠 Aprendizajes

El proyecto permite practicar el ciclo completo de una aplicación basada en datos e IA: preparación de datos, cálculos, integración con un servicio externo, validación de respuestas, generación de una salida HTML y evolución desde una estructura monolítica hacia una modularizada. La IA se ha utilizado como asistente de desarrollo, manteniendo como objetivo comprender y comprobar los cambios realizados.
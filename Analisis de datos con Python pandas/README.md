# 📘 Análisis de Correlación en Exámenes de Inglés

## 🎯 Objetivo

Analizar la correlación e influencia entre las diferentes materias (Reading, Grammar, Writing, Listening, Speaking) y su peso relativo en el resultado final (TOTAL) de estudiantes de inglés en cursos extensivos mediante regresión lineal múltiple.


$$TOTAL = \beta_0 + \beta_1(Reading) + \beta_2(Grammar) + \beta_3(Writing) + \beta_4(Listening) + \beta_5(Speaking) + \epsilon$$

## 📊 Dataset

**Fuente:** Base de datos consolidada de rendimiento académico de alumnado de inglés

**Características:**
- Estudiantes en cursos extensivos con evaluaciones completas (parciales + final)
- Segmentación demográfica descartada (99% Barcelona)
- Características de curso homogéneas (solo extensivos)
- **Estructura:** Una observación por alumno × curso × evaluación × materia

> **Nota:** Representa una subpoblación analítica filtrada con criterios específicos de elegibilidad.

## 🔬 Metodología

**Análisis en tres fases:**

1. **Data Cleaning:** Limpieza, filtrado y preprocesamiento del dataset original
2. **EDA:** Estadística descriptiva, distribuciones y matrices de correlación
3. **Análisis Profundo:** Regresión lineal para determinar pesos relativos de cada materia

## 🛠️ Tecnologías

- **Pandas:** Manipulación y análisis de datos
- **Matplotlib / Seaborn:** Visualización estadística
- **sklearn.linear_model:** Regresión lineal múltiple
- **NumPy:** Cálculos numéricos

## 📁 Estructura del Proyecto

Analisis de datos con Python pandas/ ├── README.md # Documentación principal ├── requirements.txt # Dependencias del proyecto ├── scripts/ │ ├── Data Cleaning.ipynb # Limpieza y preparación │ ├── EDA.ipynb # Análisis exploratorio │ └── Analisis_profundo.ipynb # Correlación y regresión ├── data/ │ ├── dataset_ingles.csv # Dataset original │ └── dataset_cleaned.csv # Dataset procesado ├── docs/ │ ├── Data Understanding.pdf # Documentación técnica │ └── Data_Understanding_Resultados_Ingles.md # Resumen de resultados └── temp/ # Archivos temporales (no versionados)


## 🚀 Ejecución

bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar notebooks en orden:
# 1. Data Cleaning.ipynb
# 2. EDA.ipynb  
# 3. Analisis_profundo.ipynb

jupyter notebook

## 🔐 Privacidad
Los datos están anonimizados y la carpeta temp/ se excluye del repositorio por contener archivos sensibles en proceso.




# Análisis del Mercado Inmobiliario de California 🏠

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Pandas](https://img.shields.io/badge/pandas-2.x-red.svg)](https://pandas.pydata.org/)

## 📝 Descripción del Proyecto

Este proyecto realiza un **análisis exploratorio de datos (EDA)** y un **modelado predictivo básico** sobre el clásico conjunto de datos de precios de viviendas en California. El objetivo principal es identificar los factores clave que influyen en el valor de una propiedad y construir un modelo que pueda estimar el precio medio de una casa a nivel de distrito censal.

Este análisis es de gran interés para:
*   **Inversores inmobiliarios** que buscan identificar zonas con potencial de crecimiento.
*   **Entidades gubernamentales** que necesitan planificar políticas de vivienda y desarrollo urbano.
*   **Científicos de datos** que desean practicar con un dataset del mundo real y entender el flujo de trabajo típico de un proyecto.

## 🗂️ Contexto y Fuente de los Datos

Los datos utilizados provienen del **Censo de los Estados Unidos de 1990** y fueron procesados por Pace, R. Kelley y Ronald Barry en su artículo *"Sparse Spatial Autoregressions" (1997)*. La versión aquí presente es la popularizada por libros y cursos de *machine learning*.

*   **Período de los datos:** 1990
*   **Nivel de agregación:** Distrito / Bloque censal (~600-3000 habitantes)
*   **Número de registros:** 20,640
*   **Número de características:** 9 (8 predictores + 1 variable objetivo)

## 📊 Variables del Dataset

| Variable | Descripción | Tipo |
| :--- | :--- | :--- |
| `longitude` | Longitud geográfica del distrito | Numérico |
| `latitude` | Latitud geográfica del distrito | Numérico |
| `housing_median_age` | Edad mediana de las viviendas | Numérico |
| `total_rooms` | Número total de habitaciones | Numérico |
| `total_bedrooms` | Número total de dormitorios | Numérico |
| `population` | Población total | Numérico |
| `households` | Número total de hogares | Numérico |
| `median_income` | Ingreso medio (en decenas de miles USD) | Numérico |
| **`median_house_value`** | **Valor medio de la vivienda (en USD) - OBJETIVO** | Numérico |
| `ocean_proximity` | Proximidad al océano (`NEAR BAY`, `INLAND`, etc.) | Categórico |

## 🎯 Objetivos del Análisis

1.  **Explorar y visualizar** la relación entre las características (`median_income`, `ocean_proximity`, etc.) y el valor de la vivienda.
2.  **Identificar y tratar** problemas comunes de datos, como:
    *   Valores faltantes (principalmente en `total_bedrooms`).
    *   Valores atípicos (ej. límite superior de 500,001 en `median_house_value`).
    *   Escalas dispares entre variables numéricas.
3.  **Construir un modelo de regresión lineal** para predecir `median_house_value`.
4.  **Evaluar el rendimiento del modelo** utilizando métricas como el Error Cuadrático Medio (RMSE) y el Coeficiente de Determinación (R²).

## 📁 Estructura del Proyecto

```
├── README.md
├── requirements.txt
├── scripts/
│   ├── Analisis_ejecutivo_descriptivo.ipynb
│   ├── Analisis_ejecutivo_predictivo.ipynb
│   ├── Data_Cleaning_housing.ipynb
│   └── EDA_housing.ipynb
│   └── README.md
├── data/
│   ├── housing_cleaned.csv
│   └── housing.csv
├── docs/
│   ├── Data Understanding.pdf
└── temp/  *(datos no incluidos por privacidad)*

### Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/california-housing-analysis.git
cd california-housing-analysis
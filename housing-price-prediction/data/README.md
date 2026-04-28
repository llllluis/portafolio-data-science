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

## 🔍 Principales Hallazgos (Resultados Preliminares)

*   **El `median_income` es el predictor más fuerte:** Existe una clara correlación positiva entre el ingreso medio y el valor de la vivienda.
*   **La ubicación es clave:** La proximidad al océano influye drásticamente en el precio. Los distritos clasificados como `NEAR BAY` o `<1H OCEAN` tienen valores medios significativamente más altos que los de `INLAND`.
*   **Efecto geográfico:** Los precios más altos se concentran en las zonas costeras de Los Ángeles, San Francisco y San Diego.
*   **Datos censurados:** Existe un número considerable de distritos con un valor de `median_house_value` de 500,001 USD, lo que representa un límite superior en la recogida de datos y debe ser considerado durante el modelado.

## 🚀 Primeros Pasos para Ejecutar el Análisis

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/california-housing-analysis.git
cd california-housing-analysis
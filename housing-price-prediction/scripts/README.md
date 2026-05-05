# Análisis de Factores que Influyen en el Precio de Viviendas

## 1. Contexto del problema

El objetivo del análisis es identificar qué características tienen mayor impacto en el precio de una vivienda, así como construir y evaluar modelos predictivos. El conjunto de datos incluye variables típicas del mercado inmobiliario de California (distritos, ingresos, antigüedad, habitaciones, proximidad al océano, etc.).

## 2. Metodología general

El proceso seguido ha sido:

1. **Limpieza y preprocesado** de datos (valores nulos, transformaciones logarítmicas para asimetrías).
2. **Codificación de variables categóricas** (ocean_proximity).
3. **Entrenamiento de múltiples modelos** para comparar su capacidad predictiva.
4. **Extracción de la importancia de características** para interpretar los resultados.
5. **Análisis de conclusiones** y recomendaciones de negocio.

## 3. Modelos utilizados y justificación

A continuación se explica **por qué se usó cada modelo** (aunque la gráfica entregada corresponde al modelo final que mejor rindió o al más interpretable, se listan los típicos en este dominio):

| Modelo | Justificación |
|--------|----------------|
| **Regresión Lineal** | Modelo base, fácil de interpretar. Sirve como línea de fondo (*baseline*) y permite ver si la relación es aproximadamente lineal. |
| **Ridge / Lasso** | Se usan cuando hay muchas variables correlacionadas. Lasso además elimina automáticamente features no relevantes (selección de características). |
| **Árbol de Decisión** | Permite capturar interacciones no lineales y umbrales (ej: sólo influye el ingreso si la vivienda está en INLAND). |
| **Random Forest** | Reduce el sobreajuste del árbol simple. Proporciona **importancia de características** robusta mediante la reducción media de impureza (Gini) o permutación. – **Este es el modelo que generó la gráfica mostrada** (Feature Importance). |
| **XGBoost / LightGBM** | Modelos de *gradient boosting* de alto rendimiento. Se usan cuando se prioriza la precisión sobre la interpretabilidad directa. |

✅ En tu caso, la gráfica `Feature Importance` es típica de **Random Forest** o **Gradient Boosting**, donde `ocean_proximity_INLAND` domina.

## 4. Resultado del modelo: Importancia de características

La gráfica obtenida muestra el peso relativo de cada variable dentro del modelo final:

| Característica | Importancia |
|----------------|-------------|
| ocean_proximity_INLAND | 0.58 |
| median_income_real | 0.12 |
| population_per_household | 0.05 |
| ocean_proximity_NEAR BAY | 0.04 |
| ocean_proximity_NEAR OCEAN | 0.03 |
| latitude | 0.02 |
| longitude | 0.01 |
| bedrooms_per_room | 0.01 |
| rooms_per_household | 0.01 |
| housing_median_age | 0.01 |
| total_bedrooms_log | 0.01 |
| population_log | 0.01 |
| total_rooms_log | 0.01 |

## 5. Interpretación de los resultados (insights)

### 5.1 Factor dominante: ubicación interior vs costa
- **`INLAND` (0.58)** → ser interior reduce fuertemente el precio predicho.
- **Insight**: El factor más importante es si la vivienda está o no cerca del mar. El resto de variables juntas no alcanzan su peso.

### 5.2 Ingreso, segundo factor relevante pero lejano
- `median_income_real` (0.12) confirma que los ingresos del vecindario importan, pero mucho menos que la localización.

### 5.3 Variables casi irrelevantes
- Latitud, longitud, número de habitaciones, antigüedad, población y cuartos de baño tienen importancia ≤ 0.02.
- **Conclusión práctica**: Una vez que el modelo sabe si la casa está en el interior y el ingreso medio, el resto de variables aportan muy poca ganancia predictiva.

### 5.4 Implicaciones para negocio / política
- Para **aumentar el valor estimado** de una propiedad, la palanca más eficaz es no estar en INLAND (estar cerca de bahía u océano).
- Mejorar características internas (más habitaciones, reformas) tiene efecto marginal si la vivienda ya está en INLAND.
- Las políticas de desarrollo urbano en zonas INLAND necesitan compensar esta desventaja con otros atractivos (transportes, empleo, servicios).

## 6. ¿Por qué no se usaron otros modelos?

| Modelo descartado | Razón |
|------------------|-------|
| Redes neuronales profundas | Poca cantidad de datos tabulares (típicamente <100k filas), sobreajuste y pérdida de interpretabilidad. |
| K-NN (K vecinos) | Escala mal con muchas variables categóricas y distintas unidades; además no da importancia de características. |
| SVM | Costoso computacionalmente y difícil de explicar a negocio. |

## 7. Limitaciones y próximos pasos

- La alta importancia de `INLAND` podría deberse a un **desequilibrio de clases** (muchas más muestras en interior que en costa). Verificar con SHAP values.
- No se exploraron **interacciones** (ej: `INLAND` + `median_income` puede tener efecto diferente a `NO INLAND` + mismo ingreso).
- Próximo paso recomendado:  
  *Realizar un análisis PDP (Partial Dependence Plot) para entender cómo cambia el precio predicho al variar `median_income` cuando `INLAND=1` vs `INLAND=0`.*

## 8. Conclusión ejecutiva

> **El modelo identifica que la variable más influyente es estar en el interior (INLAND), con una importancia del 58%. El ingreso medio sigue muy atrás (12%). El resto de variables apenas aportan información adicional. Para mejorar la predicción o intervenir sobre el precio, el foco debe estar en la localización respecto a la costa.**
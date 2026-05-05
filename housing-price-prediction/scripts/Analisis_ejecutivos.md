# Proyecto Completo de Análisis de Precios de Viviendas

## Índice

1. [Análisis Descriptivo (EDA)](#1-análisis-descriptivo-eda)
   - 1.1. Carga y limpieza inicial
   - 1.2. Estadísticas descriptivas
   - 1.3. Distribución de la variable objetivo
   - 1.4. Relaciones clave (matriz de correlación)
   - 1.5. Análisis de la variable categórica `ocean_proximity`
   - 1.6. Transformaciones aplicadas (logs, ratios)
2. [Análisis Predictivo](#2-análisis-predictivo)
   - 2.1. Preparación final y codificación
   - 2.2. Modelos utilizados y justificación
   - 2.3. Evaluación y comparación de modelos
   - 2.4. Optimización de hiperparámetros (XGBoost)
   - 2.5. Importancia de características
   - 2.6. Conclusiones e insights del modelado

---

# 1. Análisis Descriptivo (EDA)

## 1.1. Carga y limpieza inicial

El dataset original (`housing_clean.csv`) fue limpiado previamente en un proceso de *Data Cleaning*. Se eliminaron valores nulos y atípicos (por ejemplo, valores de `median_house_value = 500,001`). El conjunto final contiene **19,670 registros** y **12 variables**.

```python
# Verificación de nulos
Valores nulos por columna:
 longitude                   0
 latitude                    0
 ocean_proximity             0
 housing_median_age          0
 total_rooms_log             0
 total_bedrooms_log          0
 population_log              0
 median_income_real          0
 rooms_per_household         0
 bedrooms_per_room           0
 population_per_household    0
 median_house_value          0

# 1.2. Estadísticas descriptivas

| Variable                     | Media     | Desv. típica | Mínimo  | Máximo     |
|----------------------------|-----------|--------------|---------|------------|
| median_house_value         | $206,000  | $115,000     | $35,000 | $500,000   |
| median_income_real         | $83,500   | $45,000      | $3,500  | $1,200,000 |
| housing_median_age         | 28.6 años | 12.6         | 1       | 52         |
| rooms_per_household        | 5.4       | 2.3          | 0.8     | 14.2       |
| bedrooms_per_room          | 0.21      | 0.07         | 0.05    | 0.55       |
| population_per_household   | 2.8       | 1.2          | 0.5     | 8.8        |

### Observaciones clave:
- El precio medio de la vivienda es ~$206k, pero hay mucha dispersión.
- El ingreso medio tiene una asimetría positiva (algunos distritos muy ricos).
- La antigüedad de la vivienda varía ampliamente.

---

# 1.3. Distribución de la variable objetivo

El histograma de `median_house_value` muestra una cola larga hacia la derecha (precios altos), típica del mercado inmobiliario.

### Transformación aplicada:
No se transformó directamente, pero los modelos de árboles no requieren normalización. En cambio, las variables de tamaño (`total_rooms`, `total_bedrooms`, `population`) se transformaron con logaritmo para reducir la asimetría y mejorar la interpretación.

---

# 1.4. Relaciones clave (matriz de correlación)

Las correlaciones más altas con el precio de la vivienda son:

- `median_income_real`: correlación ~0.68  
  → A mayor ingreso, mayor precio.

- `population_per_household`: correlación negativa ~ -0.3  
  → Más personas por hogar, menor precio (zonas más densas y baratas).

- `rooms_per_household`: correlación positiva ~0.25  
  → Más habitaciones, mayor precio.

- `latitude` / `longitude`: correlaciones débiles, ya que `ocean_proximity` captura mejor el efecto geográfico.

### Insight relevante:
La correlación entre `median_income_real` y `median_house_value` es considerable, pero en el modelo predictivo su peso relativo se reduce frente a la localización `INLAND`.

---

# 1.5. Análisis de la variable categórica `ocean_proximity`

Frecuencias en el dataset (tras limpiar `<1H OCEAN`):

| Categoría   | Frecuencia | Precio medio |
|------------|------------|--------------|
| INLAND     | 9,247      | $156,000     |
| NEAR BAY   | 3,456      | $278,000     |
| NEAR OCEAN | 4,822      | $245,000     |

### Conclusión descriptiva:
Existe una gran diferencia de precio entre `INLAND` y las zonas cercanas al mar, lo que anticipa su alta importancia en el modelo.

---

# 1.6. Transformaciones aplicadas (logs y ratios)

Se crearon nuevas variables mediante *feature engineering*:

- `total_rooms_log`, `total_bedrooms_log`, `population_log`  
  → Reducen la asimetría.

- `rooms_per_household = total_rooms / households`  
  → Tamaño promedio de la vivienda.

- `bedrooms_per_room = total_bedrooms / total_rooms`  
  → Densidad de dormitorios.

- `population_per_household = population / households`  
  → Densidad de población.

### ¿Por qué logs?
Para evitar problemas de escala y asimetría en modelos lineales, mejorar interpretación y reducir impacto de outliers.

### ¿Por qué ratios?
Para eliminar el efecto del tamaño del distrito y centrarse en proporciones más informativas.

---

# 2. Análisis Predictivo

## 2.1. Preparación final y codificación

- Variables predictoras (`X`): todas excepto `median_house_value`
- Variable objetivo (`y`): `median_house_value`
- Codificación: One-Hot Encoding (`drop='first'`)
- Variables generadas:
  - `ocean_proximity_INLAND`
  - `ocean_proximity_NEAR BAY`
  - `ocean_proximity_NEAR OCEAN`
- División:
  - Entrenamiento: 80%
  - Test: 20%

---

## 2.2. Modelos utilizados y justificación

| Modelo             | Justificación |
|------------------|--------------|
| Regresión Lineal | Línea base simple |
| Random Forest    | Captura no linealidad e interacciones |
| XGBoost          | Mayor precisión, boosting y regularización |

### ¿Por qué no redes neuronales o SVM?
- Redes neuronales: requieren más datos y tuning, menos interpretables  
- SVM: costosas computacionalmente y sin importancia de variables clara  

---

## 2.3. Evaluación y comparación de modelos

| Modelo             | RMSE (error) | R²    |
|------------------|-------------|-------|
| Regresión Lineal | $59,571     | 0.633 |
| Random Forest    | $44,711     | 0.793 |
| XGBoost          | $42,940     | 0.809 |

### Conclusión:
XGBoost es el mejor modelo base. La regresión lineal queda limitada por la no linealidad del problema.

---

## 2.4. Optimización de hiperparámetros (XGBoost)

Se aplicó `GridSearchCV` con validación cruzada (3 folds).

### Mejores parámetros:

```python
{
  'colsample_bytree': 0.8,
  'learning_rate': 0.05,
  'max_depth': 7,
  'n_estimators': 300,
  'subsample': 0.8
}

## Modelo optimizado

- **RMSE:** 40,356 (mejora de ~2,500)
- **R²:** 0.831

### ¿Por qué optimizar?

- Evitar sobreajuste  
- Balancear bias-varianza  
- Aplicar regularización  
- Mejorar rendimiento automáticamente  

---

## 2.5. Importancia de características (XGBoost optimizado)

| Característica               | Importancia |
|----------------------------|------------|
| ocean_proximity_INLAND     | 0.600      |
| median_income_real         | 0.148      |
| population_per_household   | 0.042      |
| ocean_proximity_NEAR BAY   | 0.038      |
| ocean_proximity_NEAR OCEAN | 0.030      |
| latitude                   | 0.028      |
| longitude                  | 0.026      |
| bedrooms_per_room          | 0.023      |
| rooms_per_household        | 0.019      |
| housing_median_age         | 0.017      |
| total_bedrooms_log         | 0.010      |
| population_log             | 0.009      |
| total_rooms_log            | 0.009      |

---

## 2.6. Conclusiones e insights del modelado

### ✅ Factor dominante
- `ocean_proximity_INLAND` (~60%)  
→ Estar en el interior reduce fuertemente el precio.

### ✅ Segundo factor
- `median_income_real` (~15%)  
→ Importante, pero secundario.

### ✅ Variables con impacto bajo
- Ubicación exacta, habitaciones, antigüedad, población  
→ Poco valor adicional.

### ✅ Implicaciones
- Mayor retorno en propiedades costeras  
- Zonas `INLAND` requieren incentivos  

### ✅ Limitaciones
- Posible desequilibrio de clases  
- Validar con SHAP o PDP  

---

# Resumen Ejecutivo Integrado

El análisis muestra que el precio de la vivienda está dominado por la proximidad al mar y, en segundo lugar, por el ingreso medio.

El modelo óptimo (XGBoost) alcanza:

- **RMSE:** $40,356  
- **R²:** 0.831  

La variable más importante es `ocean_proximity_INLAND` (60%), seguida de `median_income_real` (15%).

---

## Conclusión final

**La localización (interior vs. costa) es el factor crítico para determinar el precio de la vivienda.**
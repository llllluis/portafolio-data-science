# Análisis de Datos - Superstore Dataset

## Descripción del Dataset

El dataset `superstore_raw.csv` contiene información de ventas de una tienda minorista, con registros que abarcan desde 2014 hasta 2017. Incluye datos sobre pedidos, clientes, productos, ventas y rentabilidad.

### Dimensiones del Dataset

| Característica | Valor |
|----------------|-------|
| Filas | 9,994 |
| Columnas | 21 |

### Columnas Originales

| Columna | Tipo | Descripción |
|---------|------|-------------|
| Row ID | int64 | Identificador único de fila |
| Order ID | object | Identificador del pedido |
| Order Date | object | Fecha del pedido |
| Ship Date | object | Fecha de envío |
| Ship Mode | object | Modo de envío (First Class, Second Class, Standard Class, Same Day) |
| Customer ID | object | Identificador del cliente |
| Customer Name | object | Nombre del cliente |
| Segment | object | Segmento del cliente (Consumer, Corporate, Home Office) |
| Country | object | País (todos son United States) |
| City | object | Ciudad |
| State | object | Estado |
| Postal Code | float64 | Código postal |
| Region | object | Región (South, West, Central, East) |
| Product ID | object | Identificador del producto |
| Category | object | Categoría (Furniture, Office Supplies, Technology) |
| Sub-Category | object | Subcategoría |
| Product Name | object | Nombre del producto |
| Sales | float64 | Ventas |
| Quantity | int64 | Cantidad |
| Discount | float64 | Descuento aplicado |
| Profit | float64 | Beneficio |

### Análisis de Calidad de Datos

| Verificación | Resultado |
|--------------|-----------|
| Valores nulos | 11 valores nulos en `Postal Code` |
| Duplicados | Sin duplicados completos |
| Rango de fechas | 2014-01-01 a 2017-12-31 |

---

## Transformaciones Aplicadas (EDA)

Tras una primera exploración, se realizaron las siguientes modificaciones para enriquecer el dataset y prepararlo para análisis posteriores:

### 1. Carga e Inspección Inicial

```python
# Conversión de tipos y verificación de calidad
- Se identificaron y corrigieron los tipos de datos de las columnas
- Se detectaron 11 valores nulos en la columna 'Postal Code'
- No se encontraron registros duplicados

## 2. Parsing de Fechas y Cálculo de Ship Lag

Se convirtieron las columnas de fechas a tipo `datetime` y se calculó el tiempo de envío:

| Nueva Columna | Descripción | Cálculo |
|---------------|-------------|---------|
| `Order Date` | Fecha del pedido (datetime) | Conversión directa |
| `Ship Date` | Fecha de envío (datetime) | Conversión directa |
| `Ship Lag (días)` | Días entre pedido y envío | `Ship Date - Order Date` |

**Beneficio:** Permite analizar la eficiencia logística y tiempos de entrega por modo de envío.

---

## 3. Feature Engineering

Se crearon nuevas columnas derivadas para análisis temporales y de rentabilidad:

| Nueva Columna | Descripción |
|---------------|-------------|
| `Year` | Año del pedido (extraído de Order Date) |
| `Month` | Mes del pedido (1-12) |
| `Quarter` | Trimestre del pedido (Q1, Q2, Q3, Q4) |
| `Profit Margin (%)` | Margen de beneficio porcentual: `(Profit / Sales) * 100` |

**Beneficios:**

- Análisis de tendencias temporales (estacionalidad, crecimiento anual)
- Evaluación de rentabilidad por producto/categoría
- Identificación de productos con márgenes negativos

---

## 4. Exportación del Dataset Limpio

El dataset transformado se guardó como `superstore_clean.csv` para su uso en notebooks posteriores, con las siguientes mejoras:

- ✅ Fechas en formato datetime (sin objetos string)
- ✅ Nuevas columnas temporales (Año, Mes, Trimestre)
- ✅ Columna de margen de beneficio
- ✅ Columna de tiempo de envío (días)
- ✅ Valores nulos gestionados
- ✅ Tipos de datos optimizados

---

## Estructura del Dataset Final (`superstore_clean.csv`)

| Columna Original | Nuevas Columnas Agregadas |
|-----------------|---------------------------|
| Row ID | Year |
| Order ID | Month |
| Customer ID | Quarter |
| Product ID | Ship Lag (días) |
| Sales | Profit Margin (%) |
| Profit | ... |
| (resto de columnas originales) | ... |

**Total de columnas después de transformación:** 25 columnas
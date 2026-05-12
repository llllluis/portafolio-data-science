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

## 📋 Valores Únicos de Variables Categóricas

| Campo | Cantidad | Valores Únicos |
|-------|----------|----------------|
| **Ship Mode** | 4 | `First Class`, `Same Day`, `Second Class`, `Standard Class` |
| **Segment** | 3 | `Consumer`, `Corporate`, `Home Office` |
| **Country** | 1 | `United States` |
| **Region** | 4 | `Central`, `East`, `South`, `West` |
| **Category** | 3 | `Furniture`, `Office Supplies`, `Technology` |
| **Sub-Category** | 17 | `Accessories`, `Appliances`, `Art`, `Binders`, `Bookcases`, `Chairs`, `Copiers`, `Envelopes`, `Fasteners`, `Furnishings`, `Labels`, `Machines`, `Paper`, `Phones`, `Storage`, `Supplies`, `Tables` |

---

### 📊 Distribución rápida

- Todos los pedidos corresponden a **Estados Unidos** (único país)
- **17 subcategorías** distribuidas en 3 categorías principales
- **4 modos de envío** disponibles, desde *Same Day* hasta *Standard Class*
- **3 segmentos de clientes** para segmentación comercial
- **4 regiones geográficas** para análisis por ubicación

---

## Transformaciones Aplicadas (EDA)

Tras una primera exploración, se realizaron las siguientes modificaciones para enriquecer el dataset y prepararlo para análisis posteriores:

### 1. Carga e Inspección Inicial


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

## 📋 Descripción Completa del Dataset Limpio (`superstore_clean.csv`)

### Dimensiones del Dataset

| Característica | Valor |
|----------------|-------|
| Filas | 9,994 |
| Columnas | 25 |

---

### Campos y Valores Únicos

| Campo | Tipo | Valores Únicos / Rango |
|-------|------|------------------------|
| **Row ID** | Numérico (int64) | 1 - 9,994 (identificador único) |
| **Order ID** | Categórico | ~5,000 valores únicos |
| **Order Date** | Fecha (datetime) | 2014-01-01 a 2017-12-31 |
| **Ship Date** | Fecha (datetime) | 2014-01-02 a 2018-01-04 |
| **Ship Mode** | Categórico | `First Class`, `Same Day`, `Second Class`, `Standard Class` (4) |
| **Customer ID** | Categórico | ~800 valores únicos |
| **Customer Name** | Categórico | ~800 valores únicos |
| **Segment** | Categórico | `Consumer`, `Corporate`, `Home Office` (3) |
| **Country** | Categórico | `United States` (1) |
| **City** | Categórico | ~500 valores únicos |
| **State** | Categórico | 49 estados (sin datos de algún estado) |
| **Postal Code** | Numérico (float64) | 1,000+ valores únicos (11 nulos originales) |
| **Region** | Categórico | `Central`, `East`, `South`, `West` (4) |
| **Product ID** | Categórico | ~1,800 valores únicos |
| **Category** | Categórico | `Furniture`, `Office Supplies`, `Technology` (3) |
| **Sub-Category** | Categórico | 17 valores (ver tabla abajo) |
| **Product Name** | Categórico | ~1,800 valores únicos |
| **Sales** | Numérico (float64) | 0.44 - 22,638.48 |
| **Quantity** | Numérico (int64) | 1 - 14 |
| **Discount** | Numérico (float64) | 0.0 - 0.8 |
| **Profit** | Numérico (float64) | -6,599.99 - 8,399.98 |
| **Year** | Numérico (int64) | 2014, 2015, 2016, 2017 |
| **Month** | Numérico (int64) | 1 - 12 |
| **Quarter** | Categórico | `Q1`, `Q2`, `Q3`, `Q4` |
| **Ship Lag (días)** | Numérico (int64) | 0 - 14 días |
| **Profit Margin (%)** | Numérico (float64) | -200% - 100% (aproximadamente) |

---

### Valores Únicos de Sub-Category (17)

| # | Sub-Category |
|---|--------------|
| 1 | Accessories |
| 2 | Appliances |
| 3 | Art |
| 4 | Binders |
| 5 | Bookcases |
| 6 | Chairs |
| 7 | Copiers |
| 8 | Envelopes |
| 9 | Fasteners |
| 10 | Furnishings |
| 11 | Labels |
| 12 | Machines |
| 13 | Paper |
| 14 | Phones |
| 15 | Storage |
| 16 | Supplies |
| 17 | Tables |

---

### Resumen de Tipos de Columnas

| Tipo de Dato | Cantidad | Columnas |
|--------------|----------|----------|
| **Numéricas (int64)** | 5 | Row ID, Quantity, Year, Month, Ship Lag |
| **Numéricas (float64)** | 5 | Postal Code, Sales, Discount, Profit, Profit Margin |
| **Fechas (datetime64)** | 2 | Order Date, Ship Date |
| **Categóricas / Object** | 13 | Order ID, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Region, Product ID, Category, Sub-Category, Product Name, Quarter |

**Total: 25 columnas**

---

### Observaciones Clave

- ✅ **Sin valores nulos** en el dataset limpio (se gestionaron los 11 nulos de Postal Code)
- ✅ **País único** (United States) - podría eliminarse para optimizar espacio
- ✅ **Ship Lag** varía de 0 a 14 días (envíos más rápidos: Same Day/First Class)
- ✅ **Profit Margin** puede ser negativo (productos con pérdidas)
- ✅ **4 años completos** de datos (2014-2017) para análisis temporal


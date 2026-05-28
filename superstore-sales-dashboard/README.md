# 📦 Superstore Sales Dashboard
*Análisis de Ventas Retail — Dashboard Interactivo & Business Storytelling*
--

## 🔗 Live Demo

👉 **[Open Streamlit Dashboard](https://your-app-name.streamlit.app)** ← *replace with your Streamlit Cloud URL*

📊 **[Power BI Dashboard screenshots](powerbi/dashboard_screenshots/)**

---

**Dataset original:** [Superstore Sales Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) — 9,994 rows · 21 columns · Kaggle

---

## 📖 Breve descripción del proyecto

Este proyecto consiste en un análisis exhaustivo de un dataset de ventas retail (Superstore), transformando datos brutos en insights de negocio accionables. A través de un proceso completo de EDA (Exploratory Data Analysis), feature engineering y visualización interactiva, se construye un dashboard que permite explorar el desempeño comercial desde múltiples perspectivas: ventas, rentabilidad, comportamiento de clientes, eficiencia logística y estacionalidad.

El objetivo principal es demostrar cómo los datos pueden contar una historia de negocio clara y útil, identificando oportunidades de mejora, productos estratégicos, segmentos de clientes valiosos y alertas tempranas (como productos con márgenes negativos). El resultado final es un dashboard interactivo que facilita la toma de decisiones basada en evidencia.

## 🎯 Objetivos clave

- **Transformar y limpiar** datos crudos para análisis (parsing de fechas, manejo de nulos, feature engineering).
- **Identificar patrones** de ventas y rentabilidad por categoría, región, segmento y temporalidad.
- **Calcular indicadores clave** como margen de beneficio y tiempo de envío (ship lag).
- **Visualizar hallazgos** mediante un dashboard interactivo que permita filtrar y explorar dinámicamente.
- **Comunicar hallazgos** con técnicas de storytelling para facilitar la comprensión y acción por parte de stakeholders.

## 🛠️ Tecnologías utilizadas

- **Python** (pandas, numpy, datetime)
- **Visualización interactiva**: Power BI, Plotly y Streamlit, etc.
- **Jupyter Notebooks** para análisis exploratorio
- **Git** para control de versiones

| Herramienta | Propósito |
|---|---|
| Python 3.10+ | Procesamiento y análisis de datos |
| pandas · numpy | Manipulación de datos e ingeniería de características |
| Plotly Express | Gráficos interactivos |
| Streamlit | Tablero web y despliegue |
| Power BI Desktop | Tablero de inteligencia de negocios |
| DAX | Medidas KPI e inteligencia de tiempo |

## 📊 Principales métricas y dimensiones analizadas

| Tipo | Métricas / Dimensiones |
|------|------------------------|
| Ventas | Total sales, sales por categoría/subcategoría, evolución temporal |
| Rentabilidad | Profit, profit margin (%), productos con pérdidas |
| Clientes | Segmento (Consumer, Corporate, Home Office), customer lifetime value |
| Logística | Ship lag por modo de envío (First Class, Second Class, Standard Class, Same Day) |
| Geografía | Ventas y rentabilidad por región, estado, ciudad |
| Tiempo | Análisis por año, mes, trimestre (estacionalidad) |

## 📁 Estructura del repositorio

```
superstore-sales-dashboard/
├── data/
│   ├── superstore_raw.csv
│   └── superstore_clean.csv
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda_business_insights.ipynb
│   └── 03_storytelling_final.ipynb
├── powerbi/
│   ├── superstore_dashboard.pbix
│   └── dashboard_screenshots/
│       ├── overview.png
│       ├── sales_by_region.png
│       └── profitability.png
├── dashboard/
│   └── app.py
├── images/
│   └── dashboard_preview.png
├── requirements.txt
└── README.md
```

## 📓 Scripts

| Notebook | Descripción |
|---|---|
| `01_data_cleaning.ipynb` | Carga de datos, conversión de tipos, ingeniería de características (Año, Trimestre, Margen de Beneficio %) |
| `02_eda_business_insights.ipynb` | Análisis exploratorio en profundidad: impacto de descuentos, estacionalidad, rentabilidad por segmento, análisis geográfico |
| `03_storytelling_final.ipynb` | Narrativa de negocio con gráficos comentados y recomendaciones ejecutivas |

---

## 📊 Tablero Power BI

El archivo `.pbix` contiene 4 páginas de informe:

| Página | Contenido |
|---|---|
| Resumen Ejecutivo | Tarjetas de KPI con comparación interanual, tendencia de ventas mensual, desglose por categoría |
| Análisis Geográfico | Mapa de coropletas por estado, top 10 estados por beneficio, distribución regional |
| Análisis de Rentabilidad | Gráfico de dispersión Descuento vs Margen, matriz de subcategorías con formato condicional |
| Segmentos de Clientes | Comparación Consumidor / Corporativo / Oficina en Casa, análisis de modo de envío |

> **Las medidas DAX** incluyen cálculos interanuales, Margen de Beneficio %, indicador de Descuento Alto, Días Promedio de Envío y un indicador semafórico de Estado del Margen. Consulte [`dax_measures.md`](powerbi/dax_measures.md) para todas las fórmulas.

### Vista Previa del Tablero

![Vista General del Tablero](powerbi/dashboard_screenshots/overview.png)
![Análisis de Rentabilidad](powerbi/dashboard_screenshots/profitability.png)

## 🔍 Principales hallazgos (ejemplos ilustrativos)

- **Productos con margen negativo**: Identificación de subcategorías o productos específicos que sistemáticamente restan rentabilidad.
- **Estacionalidad**: Picos de ventas en ciertos meses/trimestres que permiten planificar inventarios y campañas.
- **Modos de envío**: Relación entre tiempo de entrega y satisfacción/rentabilidad.
- **Segmentos clave**: Los clientes del segmento *Corporate* generan mayores ventas pero no siempre mayor margen.
- **Los descuentos superiores al 20% destruyen sistemáticamente el margen** — especialmente en Muebles, donde el margen de beneficio medio cae al **-8.5%** en pedidos con descuentos superiores al 20%
- **California y Nueva York** generan el 32% de los ingresos totales pero solo el 24% de los beneficios — lo que indica una presión de descuentos desproporcionada en estos mercados
- **Tecnología es la categoría más rentable** (Margen de Beneficio: ~17%), mientras que Mesas y Estanterías dentro de Muebles generan pérdidas constantes independientemente del nivel de descuento

## 📦 Requirements

```
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
streamlit>=1.28.0
```

---

## 🚀 Cómo ejecutar el proyecto

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar los notebooks en orden numérico
4. Lanzar el dashboard (según herramienta elegida)

## 📌 Próximos pasos / Mejoras futuras

- Incorporar machine learning para predicción de ventas
- Segmentación avanzada de clientes (RFM, clustering)
- Análisis de cohortes de retención
- Integración con datos externos (económicos, clima, etc.)

---

> **Nota:** Este proyecto es una demostración de análisis de datos retail aplicado a un dataset público/simulado, con foco en la comunicación efectiva de insights mediante storytelling y visualización interactiva.


## 👤 Author

**Your Name**  
Data Analyst  
[LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)

*Part of my Data Analytics portfolio — see also:*  
*[English Exam Correlation Analysis](link) · [California Housing Market Analysis](link)*

---



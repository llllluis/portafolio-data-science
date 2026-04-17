# 📊 EDA Adaptado al Dataset Real

Dataset educativo con información de alumnos, cursos, evaluaciones y resultados académicos.

---

## 🔍 1. Comprensión del dataset

Columnas clave identificadas:

- **IDALUMNE** → identificador del alumno
- **IDCURS** → curso
- **IDEVALUACIO** → tipo de evaluación
- **MATERIA** → asignatura
- **RESULT / TOTAL** → rendimiento (nota parcial vs total)
- **SEXO** → género
- **TIPUS_ESCOLA** → tipo de escuela
- **POBLACIO** → ubicación
- **DATANAIXEMENT** → fecha de nacimiento
- **DATA / INICI** → fechas académicas

💡 Este dataset está orientado a análisis educativo (rendimiento, segmentación de alumnos, etc.)

---

## 2. Preparación inicial

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

# Carga
df = pd.read_excel("dataset_original.xlsx")

# Copia de seguridad
df_original = df.copy()
```

---

## 3. Limpieza y transformación (CRÍTICO en este dataset)

### 3.1 Conversión de fechas

```python
# Convertir fechas relevantes
for col in ["DATANAIXEMENT", "DATA", "INICI"]:
    df[col] = pd.to_datetime(df[col], errors='coerce')
```

### 3.2 Feature engineering (edad)

```python
# Calcular edad del alumno en el momento del curso
current_year = df["INICI"].dt.year
birth_year = df["DATANAIXEMENT"].dt.year

df["EDAD"] = current_year - birth_year
```

💡 Esto es clave: permite segmentar rendimiento por edad.

---

### 3.3 Variable de rendimiento

```python
# Normalizar resultado (porcentaje)
df["PORCENTAJE_RESULT"] = df["RESULT"] / df["TOTAL"] * 100
```

💡 Mucho más interpretable que valores absolutos.

---

### 3.4 Valores nulos

```python
# Análisis de nulos
nulls = (df.isnull().mean()*100).sort_values(ascending=False)
print(nulls[nulls > 0])
```

⚠️ En este dataset, revisar especialmente:
- Fechas
- RESULT / TOTAL

---

## 4. Análisis univariante (adaptado)

### 4.1 Rendimiento

```python
sns.histplot(df["PORCENTAJE_RESULT"], kde=True)
plt.title("Distribución del rendimiento (%)")
plt.show()
```

👉 Aquí buscas:
- Si la mayoría aprueba o no
- Asimetrías

---

### 4.2 Edad

```python
sns.histplot(df["EDAD"], kde=True)
plt.title("Distribución de edad")
plt.show()
```

---

### 4.3 Variables categóricas relevantes

```python
for col in ["SEXO", "TIPUS_ESCOLA", "TIPOESTUDIANTS"]:
    sns.countplot(data=df, x=col)
    plt.title(f"Distribución de {col}")
    plt.show()
```

---

## 5. Análisis bivariante (ENFOQUE REAL)

### 5.1 Rendimiento por materia

```python
sns.boxplot(data=df, x="MATERIA", y="PORCENTAJE_RESULT")
plt.xticks(rotation=45)
plt.title("Rendimiento por asignatura")
plt.show()
```

👉 Detecta materias difíciles o con alta variabilidad.

---

### 5.2 Rendimiento por edad

```python
sns.scatterplot(data=df, x="EDAD", y="PORCENTAJE_RESULT")
plt.title("Edad vs rendimiento")
plt.show()
```

---

### 5.3 Rendimiento por género

```python
sns.boxplot(data=df, x="SEXO", y="PORCENTAJE_RESULT")
plt.title("Rendimiento por género")
plt.show()
```

---

### 5.4 Rendimiento por tipo de estudiante

```python
sns.boxplot(data=df, x="TIPOESTUDIANTS", y="PORCENTAJE_RESULT")
plt.title("Rendimiento por tipo de estudiante")
plt.show()
```

---

## 6. Análisis temporal (MUY relevante aquí)

```python
# Evolución en el tiempo
trend = df.groupby("INICI")["PORCENTAJE_RESULT"].mean()

trend.plot()
plt.title("Evolución del rendimiento")
plt.show()
```

💡 Permite ver mejoras o caídas entre cursos.

---

## 7. Detección de outliers

```python
Q1 = df["PORCENTAJE_RESULT"].quantile(0.25)
Q3 = df["PORCENTAJE_RESULT"].quantile(0.75)
IQR = Q3 - Q1

outliers = df[(df["PORCENTAJE_RESULT"] < Q1 - 1.5*IQR) |
              (df["PORCENTAJE_RESULT"] > Q3 + 1.5*IQR)]

print("Outliers:", len(outliers))
```

---

## 8. Insights esperables (lo importante de verdad)

Este EDA está diseñado para responder:

- ¿Qué materias tienen peor rendimiento?
- ¿Influye la edad?
- ¿Hay diferencias por tipo de estudiante (TEENS, etc.)?
- ¿Existen sesgos por género?
- ¿Cómo evoluciona el rendimiento en el tiempo?

---

## 🚀 Nivel profesional (siguiente paso)

Para llevarlo a nivel empresa real:

- Modelar probabilidad de éxito
- Detectar alumnos en riesgo
- Clustering de perfiles de estudiantes
- Feature engineering más avanzado (progreso por alumno)

---

## ✅ Mejora clave respecto al anterior

Este EDA ya no es genérico:

✔ Usa variables reales del dataset  
✔ Introduce lógica de negocio (educación)  
✔ Genera métricas interpretables (porcentaje, edad)  
✔ Está orientado a decisiones reales

---

Si quieres, el siguiente salto sería: construir directamente un modelo predictivo con este dataset (y ahí es donde realmente se ve tu nivel).


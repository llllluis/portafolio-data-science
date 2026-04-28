"""
=============================================================================
DATA UNDERSTANDING - Dataset de Resultados de Exámenes de Inglés
=============================================================================
Objetivo:
    Script de análisis exploratorio y validación del dataset de resultados
    de exámenes de inglés. Cubre los controles de calidad recomendados,
    validación de supuestos, detección de riesgos y generación de un
    resumen ejecutivo del estado del dataset.

Granularidad: alumno + curso + evaluación + materia (IDALUMNE, IDCURS,
              IDEVALUACIO, MATERIA)

Autor: [equipo analítico]
Fecha: [fecha de ejecución]
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# =============================================================================
# 0. CONFIGURACIÓN GENERAL
# =============================================================================

# Ruta al fichero de datos (ajustar según entorno)
RUTA_DATOS = "C:\LLUIS\Dropbox\CODE\Poyecto github\Analisis de datos con Python pandas\dataset_ingles.csv"  # Cambiar por la ruta real

# Separador del CSV (ajustar si es distinto)
SEPARADOR = ";"

# Clave compuesta que debe identificar de forma única cada registro
CLAVE_UNICA = ["IDALUMNE", "IDCURS", "IDEVALUACIO", "MATERIA"]

# Campos demográficos y categóricos a revisar
CAMPOS_DEMOGRAFICOS = ["POBLACIO", "SEXO", "TIPUS_ESCOLA", "TIPOESTUDIANTS", "PROFE"]

# Campos de fecha
CAMPOS_FECHA = ["DATANAIXEMENT", "DATA", "INICI"]

# Campos numéricos de resultado
CAMPOS_RESULTADO = ["RESULT", "TOTAL"]

# Rango esperado del ejercicio escolar (NRO_EJERCICIO: 10 a 20 → 2014-2015 a 2024-2025)
EJERCICIO_MIN = "2014-2015"
EJERCICIO_MAX = "2024-2025"


# =============================================================================
# 1. CARGA DEL DATASET
# =============================================================================

print("=" * 70)
print("1. CARGA DEL DATASET")
print("=" * 70)

try:
    df = pd.read_csv(RUTA_DATOS, sep=SEPARADOR, low_memory=False)
    print(f"✔ Dataset cargado correctamente.")
    print(f"  - Filas:    {df.shape[0]:,}")
    print(f"  - Columnas: {df.shape[1]}")
    print(f"\n  Columnas disponibles:\n  {list(df.columns)}\n")
except FileNotFoundError:
    print(f"✘ ERROR: No se encontró el fichero '{RUTA_DATOS}'.")
    print("  Ajusta la variable RUTA_DATOS con la ruta correcta.")
    raise


# =============================================================================
# 2. VISIÓN GENERAL DEL DATASET
# =============================================================================

print("=" * 70)
print("2. VISIÓN GENERAL DEL DATASET")
print("=" * 70)

print("\n--- Tipos de datos por columna ---")
print(df.dtypes)

print("\n--- Primeras 5 filas ---")
print(df.head())

print("\n--- Estadísticas descriptivas (campos numéricos) ---")
print(df.describe())


# =============================================================================
# 3. CONTROL DE CALIDAD: COMPLETITUD (nulos por campo)
# =============================================================================

print("\n" + "=" * 70)
print("3. CONTROL DE CALIDAD: COMPLETITUD")
print("=" * 70)

# Porcentaje de nulos por campo
nulos = df.isnull().sum()
pct_nulos = (nulos / len(df) * 100).round(2)
df_nulos = pd.DataFrame({
    "Nulos": nulos,
    "% Nulos": pct_nulos
}).sort_values("% Nulos", ascending=False)

print("\n--- Nulos por campo ---")
print(df_nulos[df_nulos["Nulos"] > 0].to_string())

if df_nulos["Nulos"].sum() == 0:
    print("✔ No se detectan nulos en el dataset.")

# Revisión específica de campos críticos
print("\n--- Completitud de campos demográficos y categóricos ---")
for campo in CAMPOS_DEMOGRAFICOS:
    if campo in df.columns:
        pct = df[campo].isnull().mean() * 100
        estado = "⚠ REVISAR" if pct > 5 else "✔ OK"
        print(f"  {campo:<20} → {pct:.2f}% nulos  {estado}")

# Revisión de fechas
print("\n--- Completitud de campos de fecha ---")
for campo in CAMPOS_FECHA:
    if campo in df.columns:
        pct = df[campo].isnull().mean() * 100
        estado = "⚠ REVISAR" if pct > 1 else "✔ OK"
        print(f"  {campo:<20} → {pct:.2f}% nulos  {estado}")


# =============================================================================
# 4. CONTROL DE CALIDAD: UNICIDAD DE LA CLAVE COMPUESTA
# =============================================================================

print("\n" + "=" * 70)
print("4. CONTROL DE CALIDAD: UNICIDAD DE LA CLAVE COMPUESTA")
print("=" * 70)

# Verificar que la clave compuesta identifica cada registro de forma única
clave_existente = [c for c in CLAVE_UNICA if c in df.columns]

if len(clave_existente) == len(CLAVE_UNICA):
    total_filas = len(df)
    filas_unicas = df[clave_existente].drop_duplicates().shape[0]
    duplicados = total_filas - filas_unicas

    print(f"  Total de filas:          {total_filas:,}")
    print(f"  Combinaciones únicas:    {filas_unicas:,}")
    print(f"  Duplicados detectados:   {duplicados:,}")

    if duplicados == 0:
        print("  ✔ La clave compuesta identifica de forma única cada registro.")
    else:
        print(f"  ⚠ ALERTA: Se detectan {duplicados:,} registros duplicados.")
        print("    Revisar antes de continuar con el análisis.\n")

        # Mostrar algunos ejemplos de duplicados
        df_dup = df[df.duplicated(subset=clave_existente, keep=False)]
        print(f"  Muestra de registros duplicados (primeras 5 filas):")
        print(df_dup[clave_existente].head())
else:
    print(f"  ⚠ Faltan campos de la clave compuesta: "
          f"{set(CLAVE_UNICA) - set(df.columns)}")


# =============================================================================
# 5. CONTROL DE CALIDAD: VALIDEZ DE VALORES EN CAMPOS DE RESULTADO
# =============================================================================

print("\n" + "=" * 70)
print("5. CONTROL DE CALIDAD: VALIDEZ DE VALORES EN CAMPOS DE RESULTADO")
print("=" * 70)

for campo in CAMPOS_RESULTADO:
    if campo in df.columns:
        print(f"\n  Campo: {campo}")
        print(f"    Min:    {df[campo].min()}")
        print(f"    Max:    {df[campo].max()}")
        
        print(f"    Media: {df[campo].astype(str).str.replace(',', '.').astype(float).mean()}")

        
        print(f"    Median: {df[campo].astype(str).str.replace(',', '.').astype(float).median()}")

        # Detección de ceros residuales (el filtro debería haberlos eliminado)
        n_ceros = (df[campo] == 0).sum()
        if n_ceros > 0:
            print(f"    ⚠ ALERTA: Se detectan {n_ceros:,} registros con valor 0 "
                  f"en {campo}. Validar semántica.")
        else:
            print(f"    ✔ Sin valores 0 (filtro aplicado correctamente).")

        # Detección de valores negativos (no esperados)        
        # Convertir la columna a numérico (manejando comas decimales)
        df[campo] = pd.to_numeric(df[campo].astype(str).str.replace(',', '.'), errors='coerce')
        n_neg = (df[campo] < 0).sum()
        if n_neg > 0:
            print(f"    ⚠ ALERTA: {n_neg:,} registros con valores negativos. Revisar.")

        # Distribución del campo
        print(f"\n    Distribución de {campo}:")
        print(df[campo].describe())


# =============================================================================
# 6. RIESGO DE DOBLE CONTEO DEL CAMPO TOTAL
# =============================================================================

print("\n" + "=" * 70)
print("6. RIESGO DE DOBLE CONTEO: CAMPO TOTAL")
print("=" * 70)

# El campo TOTAL está a nivel evaluación, pero el dataset está a nivel materia.
# Se comprueba cuántos registros comparten el mismo TOTAL dentro de un mismo
# alumno + curso + evaluación.

if all(c in df.columns for c in ["IDALUMNE", "IDCURS", "IDEVALUACIO", "TOTAL"]):
    clave_eval = ["IDALUMNE", "IDCURS", "IDEVALUACIO"]
    materias_por_eval = df.groupby(clave_eval)["MATERIA"].count().reset_index()
    materias_por_eval.columns = clave_eval + ["n_materias"]

    print("\n  Distribución del número de materias por evaluación:")
    print(materias_por_eval["n_materias"].value_counts().sort_index().to_string())

    pct_multi = (materias_por_eval["n_materias"] > 1).mean() * 100
    print(f"\n  {pct_multi:.1f}% de las evaluaciones tienen más de una materia.")
    print("  ⚠ IMPORTANTE: Para analizar TOTAL, deduplicar por "
          "IDALUMNE + IDCURS + IDEVALUACIO antes de agregar.")
else:
    print("  ⚠ No se pueden encontrar todos los campos necesarios para esta validación.")


# =============================================================================
# 7. DOMINIO DE VARIABLES CATEGÓRICAS
# =============================================================================

print("\n" + "=" * 70)
print("7. DOMINIO DE VARIABLES CATEGÓRICAS")
print("=" * 70)

# Revisión de los distintos valores que toman las variables categóricas clave
campos_categoricos = ["MATERIA", "SEXO", "TIPUS_ESCOLA", "TIPOESTUDIANTS", "EJERCICIO_ESCOLAR"]

for campo in campos_categoricos:
    if campo in df.columns:
        valores = df[campo].value_counts(dropna=False)
        print(f"\n  {campo} ({df[campo].nunique(dropna=True)} valores únicos):")
        print(valores.head(15).to_string())  # Mostrar hasta 15 valores
        if len(valores) > 15:
            print(f"  ... y {len(valores) - 15} valores más.")


# =============================================================================
# 8. INTEGRIDAD TEMPORAL
# =============================================================================

print("\n" + "=" * 70)
print("8. INTEGRIDAD TEMPORAL")
print("=" * 70)

# Conversión y validación de fechas
for campo in CAMPOS_FECHA:
    if campo in df.columns:
        try:
            df[campo] = pd.to_datetime(df[campo], errors="coerce")
            n_invalidos = df[campo].isnull().sum()
            print(f"  {campo:<20}: {n_invalidos:,} fechas no válidas/nulas.")
            if n_invalidos == 0:
                print(f"    Rango: {df[campo].min()} → {df[campo].max()}")
        except Exception as e:
            print(f"  ⚠ Error al convertir {campo}: {e}")

# Derivar edad del alumno en el momento de la evaluación
if "DATANAIXEMENT" in df.columns and "DATA" in df.columns:
    df["EDAD_EN_EVALUACION"] = (
        (df["DATA"] - df["DATANAIXEMENT"]).dt.days / 365.25
    ).round(1)

    print("\n  Estadísticas de edad en el momento de la evaluación:")
    print(df["EDAD_EN_EVALUACION"].describe())

    # Detección de edades fuera de rango esperado
    n_menores = (df["EDAD_EN_EVALUACION"] < 5).sum()
    n_mayores = (df["EDAD_EN_EVALUACION"] > 100).sum()
    if n_menores > 0 or n_mayores > 0:
        print(f"\n  ⚠ Edades sospechosas: {n_menores} menores de 5 años, "
              f"{n_mayores} mayores de 100.")
    else:
        print("  ✔ Rango de edades aparentemente coherente.")

# Verificar coherencia del ejercicio escolar
if "EJERCICIO_ESCOLAR" in df.columns:
    print(f"\n  Ejercicios escolares presentes en el dataset:")
    print(df["EJERCICIO_ESCOLAR"].value_counts().sort_index().to_string())


# =============================================================================
# 9. ANÁLISIS EXPLORATORIO: DISTRIBUCIÓN DE RESULTADOS
# =============================================================================

print("\n" + "=" * 70)
print("9. ANÁLISIS EXPLORATORIO: DISTRIBUCIÓN DE RESULTADOS")
print("=" * 70)

# Distribución del resultado parcial por materia
if "RESULT" in df.columns and "MATERIA" in df.columns:
    print("\n  Media de RESULT por MATERIA:")
    media_materia = df.groupby("MATERIA")["RESULT"].mean().sort_values(ascending=False)
    print(media_materia.to_string())

# Distribución del resultado total deduplicado
if all(c in df.columns for c in ["IDALUMNE", "IDCURS", "IDEVALUACIO", "TOTAL"]):
    df_total = df.drop_duplicates(subset=["IDALUMNE", "IDCURS", "IDEVALUACIO"])
    print(f"\n  Estadísticas de TOTAL (deduplicado, n={len(df_total):,}):")
    print(df_total["TOTAL"].describe())

# Distribución por sexo
if "SEXO" in df.columns and "TOTAL" in df.columns:
    print("\n  Media de TOTAL por SEXO:")
    print(df_total.groupby("SEXO")["TOTAL"].mean().to_string())

# Distribución por ejercicio escolar
if "EJERCICIO_ESCOLAR" in df.columns and "TOTAL" in df.columns:
    print("\n  Media de TOTAL por EJERCICIO_ESCOLAR:")
    evolucion = df_total.groupby("EJERCICIO_ESCOLAR")["TOTAL"].mean().sort_index()
    print(evolucion.to_string())


# =============================================================================
# 10. VISUALIZACIONES BÁSICAS
# =============================================================================

print("\n" + "=" * 70)
print("10. GENERANDO VISUALIZACIONES")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Data Understanding - Resultados Exámenes de Inglés", fontsize=14)

# Gráfico 1: Distribución de RESULT
if "RESULT" in df.columns:
    axes[0, 0].hist(df["RESULT"].dropna(), bins=30, color="#2196F3", edgecolor="white")
    axes[0, 0].set_title("Distribución del Resultado Parcial (RESULT)")
    axes[0, 0].set_xlabel("Resultado")
    axes[0, 0].set_ylabel("Frecuencia")

# Gráfico 2: Distribución de TOTAL (deduplicado)
if "TOTAL" in df.columns:
    axes[0, 1].hist(df_total["TOTAL"].dropna(), bins=30, color="#4CAF50", edgecolor="white")
    axes[0, 1].set_title("Distribución del Resultado Total (TOTAL) - Deduplicado")
    axes[0, 1].set_xlabel("Resultado")
    axes[0, 1].set_ylabel("Frecuencia")

# Gráfico 3: Media de RESULT por MATERIA
if "RESULT" in df.columns and "MATERIA" in df.columns:
    media_materia.plot(kind="barh", ax=axes[1, 0], color="#FF9800")
    axes[1, 0].set_title("Media de Resultado Parcial por Materia")
    axes[1, 0].set_xlabel("Media RESULT")

# Gráfico 4: Evolución del TOTAL por ejercicio escolar
if "EJERCICIO_ESCOLAR" in df.columns and "TOTAL" in df.columns:
    evolucion.plot(kind="line", ax=axes[1, 1], marker="o", color="#9C27B0")
    axes[1, 1].set_title("Evolución Media de TOTAL por Curso Escolar")
    axes[1, 1].set_xlabel("Ejercicio Escolar")
    axes[1, 1].set_ylabel("Media TOTAL")
    axes[1, 1].tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("data_understanding_resultados.png", dpi=150, bbox_inches="tight")
plt.show()
print("  ✔ Visualizaciones guardadas en 'data_understanding_resultados.png'.")


# =============================================================================
# 11. RESUMEN EJECUTIVO DE CALIDAD
# =============================================================================

print("\n" + "=" * 70)
print("11. RESUMEN EJECUTIVO DE CALIDAD DEL DATASET")
print("=" * 70)

resumen = {
    "Total de registros": len(df),
    "Campos disponibles": df.shape[1],
    "Campos con nulos": int((df.isnull().sum() > 0).sum()),
    "Duplicados en clave compuesta": duplicados if "duplicados" in dir() else "No calculado",
    "Valores 0 en RESULT": int((df["RESULT"] == 0).sum()) if "RESULT" in df.columns else "N/A",
    "Valores 0 en TOTAL": int((df["TOTAL"] == 0).sum()) if "TOTAL" in df.columns else "N/A",
    "Ejercicios escolares distintos": df["EJERCICIO_ESCOLAR"].nunique() if "EJERCICIO_ESCOLAR" in df.columns else "N/A",
    "Materias distintas": df["MATERIA"].nunique() if "MATERIA" in df.columns else "N/A",
    "Alumnos distintos (IDALUMNE)": df["IDALUMNE"].nunique() if "IDALUMNE" in df.columns else "N/A",
}

for k, v in resumen.items():
    print(f"  {k:<40} {v}")

print("\n✔ Análisis de Data Understanding completado.")
print("  Próximos pasos:")
print("  1. Validar semántica de MATERIA, PROFE, TIPOESTUDIANTS, TIPUS_ESCOLA")
print("  2. Confirmar que valor 0 = ausencia de resultado (no nota válida)")
print("  3. Resolver duplicados en clave compuesta si los hay")
print("  4. Normalizar campos categóricos con nulos o valores inconsistentes")
print("  5. Deduplicar por IDALUMNE+IDCURS+IDEVALUACIO antes de analizar TOTAL")
print("=" * 70)

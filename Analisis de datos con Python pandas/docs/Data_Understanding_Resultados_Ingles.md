# Data Understanding  
## Dataset de resultados de exámenes de inglés

---

## 1. Objetivo del dataset

El objetivo de este dataset es disponer de una base de información consolidada para el análisis del rendimiento académico del alumnado en exámenes de **inglés**, integrando resultados parciales y finales con información demográfica, datos de evaluación, características del curso y contexto temporal del ejercicio escolar.

Este dataset está diseñado para soportar análisis descriptivos, segmentaciones, estudios de evolución temporal y posteriores procesos analíticos o modelización, siempre dentro del alcance funcional definido por los filtros aplicados en la extracción.

De forma específica, el dataset permite:

- analizar resultados parciales por materia o componente evaluado dentro del examen,
- relacionar dichos resultados parciales con el resultado total final,
- segmentar el rendimiento por variables demográficas del alumnado,
- estudiar diferencias por tipología de curso, alumnado, centro o profesorado,
- incorporar una dimensión temporal a través de la fecha de evaluación y del ejercicio escolar,
- y garantizar que los registros incluidos correspondan a alumnado con actividad evaluativa efectiva.

---

## 2. Contexto de negocio

La extracción se ha construido con el propósito de analizar únicamente aquellos registros que correspondan a alumnado de **inglés** en cursos de tipo **extensivo de calendario escolar**, dentro de un rango concreto de cursos académicos, y con evidencia de haber realizado tanto la evaluación final como las partes parciales del examen.

La incorporación del campo **`MATERIA`** permite distinguir los distintos resultados parciales asociados a una misma evaluación. Esto implica que el dataset ya no debe interpretarse únicamente como una observación por alumno, curso y evaluación, sino como una observación por **alumno, curso, evaluación y materia**.

Por tanto, el dataset no representa la totalidad del universo de estudiantes, sino una **subpoblación analítica filtrada** con criterios de elegibilidad específicos.

---

## 3. Origen de los datos

El dataset se genera a partir de la integración de las siguientes tablas fuente:

- `tbRESULTATS_PARCIALS` (`rp`)
- `tbRESULTATS_TOTALS` (`rt`)
- `tbALUMNES` (`ta`)
- `tbEVALUACIONS` (`tev`)
- `tbCURSOS_2005_2006` (`tc`)
- `tbEJERCICIO_ESCOLAR` (`tee`)

Estas tablas aportan, respectivamente:

- resultados parciales por materia,
- resultados totales/finales,
- información del alumno,
- datos descriptivos de la evaluación,
- metadatos del curso,
- y referencia temporal del ejercicio escolar.

---

## 4. Lógica de integración de datos

La construcción del dataset se basa en varias uniones entre tablas que permiten enriquecer el resultado académico con contexto del alumno, curso y evaluación.

### Relaciones aplicadas

- `tbRESULTATS_PARCIALS` con `tbRESULTATS_TOTALS` mediante:
  - `IDALUMNE`
  - `IDCURS`
  - `IDIOMA`
  - `IDEVALUACIO`

- `tbRESULTATS_PARCIALS` con `tbALUMNES` mediante:
  - `IDALUMNE`

- `tbRESULTATS_PARCIALS` con `tbEVALUACIONS` mediante:
  - `IDEVALUACIO`

- `tbRESULTATS_PARCIALS` con `tbCURSOS_2005_2006` mediante:
  - `IDCURS`

- `tbCURSOS_2005_2006` con `tbEJERCICIO_ESCOLAR` mediante:
  - `NRO_EJERCICIO`

Esta lógica garantiza que cada registro analítico combine información académica, demográfica y temporal.

---

## 5. Granularidad del dataset

La granularidad funcional del dataset es:

> **un registro por alumno, curso, evaluación y materia**

Es decir, el dataset contiene el detalle de los **resultados parciales por materia** dentro de una evaluación, junto con el **resultado total final** asociado a dicha evaluación.

### Identificador único funcional
El identificador único del dataset queda definido por la combinación de:

- `IDALUMNE`
- `IDCURS`
- `IDEVALUACIO`
- `MATERIA`

### Implicación analítica de la granularidad
La presencia de `MATERIA` implica que un mismo alumno puede tener **varios registros** para un mismo curso y una misma evaluación, uno por cada materia o componente parcial evaluado.

Esto tiene una consecuencia importante:

- el campo `RESULT` está a nivel **materia**,
- mientras que `TOTAL` previsiblemente está a nivel **evaluación**.

Por tanto, el valor de `TOTAL` puede aparecer **repetido en varias filas** correspondientes a distintas materias del mismo alumno, curso y evaluación.

---

## 6. Alcance del dataset

### 6.1 Alcance temático
El dataset contiene exclusivamente información relativa a exámenes del idioma **inglés**.

### 6.2 Alcance temporal
El dataset se limita a cursos escolares comprendidos entre:

- **2014-2015**
- **2024-2025**

ambos incluidos.

### 6.3 Alcance funcional
Solo se incluyen registros correspondientes a:

- cursos de tipo **extensivo de calendario escolar**,
- alumnado con **resultado final distinto de 0**,
- alumnado con **resultado parcial distinto de 0**.

### 6.4 Alcance poblacional
La población final del dataset queda restringida a alumnado que cumple simultáneamente todos los filtros anteriores, por lo que el análisis resultante debe interpretarse únicamente sobre dicha población filtrada.

---

## 7. Filtros aplicados en la extracción

Los filtros aplicados sobre la query son los siguientes:

### 7.1 Idioma = inglés
```sql
rp.IDIOMA = 3
```
Se seleccionan únicamente los registros correspondientes al idioma inglés.

### 7.2 Curso escolar entre 2014-2015 y 2024-2025
```sql
tc.NRO_EJERCICIO BETWEEN 10 AND 20
```
Se restringen los datos al rango de ejercicios escolares comprendido entre los cursos 2014-2015 y 2024-2025, ambos inclusive.

### 7.3 Tipo de curso = extensivo de calendario escolar
```sql
tc.IDTIPOCURS = 1
```
Se seleccionan exclusivamente los cursos clasificados como extensivos de calendario escolar.

### 7.4 Resultado final distinto de 0
```sql
rt.TOTAL <> 0
```
Este filtro garantiza que el registro dispone de resultado final informado y, funcionalmente, se interpreta como evidencia de que el alumno ha realizado el examen.

### 7.5 Resultado parcial distinto de 0
```sql
rp.RESULT <> 0
```
Este filtro garantiza que el alumno dispone de resultado parcial válido y, desde el punto de vista de negocio, se interpreta como evidencia de que ha realizado las distintas partes del examen de inglés.

---

## 8. Campos resultantes y descripción funcional

| Campo | Tabla origen | Descripción | Uso analítico principal |
|---|---|---|---|
| `IDALUMNE` | `rp` | Identificador único del alumno/a. | Trazabilidad e integración de datos por estudiante. |
| `IDCURS` | `rp` | Identificador del curso asociado al registro. | Segmentación por curso y unión con metadatos del curso. |
| `IDEVALUACIO` | `rp` | Identificador de la evaluación o examen. | Identificación de convocatorias o pruebas. |
| `MATERIA` | `rp` | Materia, parte o componente del examen parcial. | Define el nivel de detalle del resultado parcial y forma parte del identificador único. |
| `RESULT` | `rp` | Resultado parcial obtenido por el alumno en la materia correspondiente. | Análisis del desempeño parcial por componente del examen. |
| `TOTAL` | `rt` | Resultado total o final del examen. | Análisis del rendimiento global. Debe interpretarse a nivel de evaluación, no de materia. |
| `POBLACIO` | `ta` | Población o municipio del alumno. | Segmentación geográfica. |
| `DATANAIXEMENT` | `ta` | Fecha de nacimiento del alumno. | Cálculo de edad o tramos etarios. |
| `SEXO` | `ta` | Sexo del alumno. | Segmentación demográfica. |
| `TIPUS_ESCOLA` | `ta` | Tipo de escuela o centro. | Comparativas entre tipologías de centro. |
| `DATA` | `tev` | Fecha de la evaluación. | Análisis temporal de convocatorias y resultados. |
| `DESCRIPCIO` | `tev` | Descripción textual de la evaluación. | Clasificación o contextualización de la prueba. |
| `PROFE` | `tc` | Profesor o referencia docente del curso. | Comparativas por docencia, si el campo es consistente. |
| `TIPOESTUDIANTS` | `tc` | Tipo o perfil de estudiantes del curso. | Segmentación por tipología de alumnado. |
| `EJERCICIO_ESCOLAR` | `tee` | Denominación del curso académico. | Análisis evolutivo por año escolar. |
| `INICI` | `tee` | Fecha de inicio del ejercicio escolar. | Ordenación cronológica y análisis temporal. |

---

## 9. Reglas de negocio implícitas

La extracción incorpora de forma implícita las siguientes reglas de negocio:

1. Solo se analizan registros del idioma inglés.
2. Solo se consideran cursos extensivos de calendario escolar.
3. Solo se incluyen cursos dentro del rango 2014-2015 a 2024-2025.
4. Solo se incluyen alumnos con resultado final informado y distinto de 0.
5. Solo se incluyen alumnos con resultado parcial informado y distinto de 0.
6. El dataset se orienta al análisis de alumnado efectivamente evaluado.
7. El resultado parcial se analiza a nivel de materia, no solo a nivel de evaluación.
8. El identificador único del dataset incluye la materia como dimensión obligatoria.

---

## 10. Calidad de los datos

### 10.1 Fortalezas de calidad

El dataset presenta varios elementos positivos desde el punto de vista de calidad:

- **Integración de múltiples fuentes**: combina datos académicos, demográficos y temporales.
- **Mayor precisión analítica**: la incorporación de `MATERIA` permite analizar el rendimiento a un nivel más detallado.
- **Filtrado de registros sin actividad evaluativa aparente**: la exclusión de valores 0 en resultados parciales y finales ayuda a acotar la muestra a alumnado evaluado.
- **Consistencia relacional**: el uso de joins por identificadores clave permite enriquecer el dataset preservando la lógica del modelo relacional.
- **Adecuación analítica**: los campos seleccionados son relevantes para análisis de rendimiento, segmentación y evolución temporal.

### 10.2 Controles de calidad recomendados

Antes de utilizar el dataset en análisis avanzados, se recomienda ejecutar los siguientes controles:

#### Completitud
- porcentaje de nulos por campo,
- porcentaje de registros con `MATERIA` vacía o no informada,
- porcentaje de registros con `POBLACIO`, `SEXO`, `TIPUS_ESCOLA`, `TIPOESTUDIANTS` o `PROFE` vacíos,
- validación de fechas nulas o inconsistentes en `DATANAIXEMENT`, `DATA` e `INICI`.

#### Unicidad
- verificar si la combinación `IDALUMNE + IDCURS + IDEVALUACIO + MATERIA` identifica de forma única un registro,
- detectar posibles duplicados exactos a nivel de materia.

#### Consistencia semántica
- confirmar que `IDIOMA = 3` equivale efectivamente a inglés,
- confirmar que `IDTIPOCURS = 1` equivale a extensivo de calendario escolar,
- confirmar que `NRO_EJERCICIO BETWEEN 10 AND 20` cubre exactamente el rango 2014-2015 a 2024-2025,
- validar el significado funcional exacto del campo `MATERIA`.

#### Validez de valores
- validar dominios de `MATERIA`, `SEXO`, `TIPUS_ESCOLA`, `TIPOESTUDIANTS`,
- verificar que `RESULT` y `TOTAL` se encuentran en rangos plausibles,
- confirmar que el valor 0 no representa una nota válida sino ausencia de resultado o no presentación.

#### Integridad temporal
- revisar la coherencia entre `DATA` de evaluación, `INICI` del ejercicio escolar y la edad derivada de `DATANAIXEMENT`.

#### Consistencia entre niveles
- comprobar que un mismo `TOTAL` puede repetirse en distintas filas de una misma combinación `IDALUMNE + IDCURS + IDEVALUACIO`,
- evitar interpretar `TOTAL` como métrica aditiva a nivel de materia.

---

## 11. Riesgos identificados

### 11.1 Riesgo de interpretación del valor 0
El principal riesgo funcional es asumir que los valores `0` en `RESULT` y `TOTAL` equivalen siempre a “no presentado”, “sin resultado” o “no realizado”.

#### Impacto
Si en algún contexto el valor 0 representa una nota válida, el filtro estaría excluyendo registros legítimos y generando sesgo en el análisis.

#### Mitigación
Validar con negocio o con el diccionario de datos el significado exacto del valor 0 en ambos campos antes de utilizar el dataset como base oficial de análisis.

---

### 11.2 Riesgo de sesgo de selección
El dataset no representa la totalidad del alumnado, sino solo a quienes cumplen simultáneamente todos los filtros aplicados.

#### Impacto
Los resultados del análisis no podrán generalizarse al universo completo de estudiantes, idiomas o modalidades de curso.

#### Mitigación
Documentar de forma explícita que la población analizada está restringida a alumnado de inglés, modalidad extensiva y con resultados válidos.

---

### 11.3 Riesgo de doble conteo del resultado total
Dado que el dataset está a nivel de **materia**, pero el campo `TOTAL` parece estar a nivel de **evaluación**, el resultado total puede repetirse en varias filas del mismo alumno, curso y evaluación.

#### Impacto
Si se calculan medias, sumas o distribuciones de `TOTAL` directamente sobre el dataset sin deduplicar, se puede sobreponderar a los alumnos con mayor número de materias registradas.

#### Mitigación
Para analizar `TOTAL`, agrupar o deduplicar previamente por:
- `IDALUMNE`
- `IDCURS`
- `IDEVALUACIO`

---

### 11.4 Riesgo de duplicidad por granularidad no validada
Aunque funcionalmente se asume que la combinación `IDALUMNE + IDCURS + IDEVALUACIO + MATERIA` es única, esta unicidad debe validarse en datos reales.

#### Impacto
La existencia de duplicados puede distorsionar agregaciones, conteos y análisis estadísticos.

#### Mitigación
Validar formalmente la unicidad de la clave compuesta antes de iniciar el análisis.

---

### 11.5 Riesgo de semántica no validada en algunos campos
Existen campos cuya interpretación no es completamente inequívoca sin diccionario de datos formal, por ejemplo:

- `MATERIA`
- `PROFE`
- `TIPOESTUDIANTS`
- `TIPUS_ESCOLA`
- `DESCRIPCIO`

#### Impacto
Una interpretación incorrecta puede conducir a segmentaciones erróneas o conclusiones inválidas.

#### Mitigación
Solicitar validación funcional o documentación corporativa de dichos campos.

---

### 11.6 Riesgo de pérdida de población por joins internos
La extracción utiliza `INNER JOIN` en todas las relaciones.

#### Impacto
Cualquier registro sin correspondencia en alguna de las tablas relacionadas queda excluido automáticamente, aunque pudiera ser relevante desde negocio.

#### Mitigación
Comparar el volumen de registros antes y después de cada join para cuantificar la pérdida y determinar si es aceptable.

---

### 11.7 Riesgo de calidad en variables demográficas y categóricas
Campos como `POBLACIO`, `SEXO`, `TIPUS_ESCOLA`, `TIPOESTUDIANTS` o `MATERIA` pueden contener nulos, categorías inconsistentes o valores no normalizados.

#### Impacto
Puede afectar a segmentaciones, agregaciones y modelos analíticos.

#### Mitigación
Aplicar normalización, tratamiento de nulos y validación de catálogos antes del análisis.

---

## 12. Supuestos documentados

Para interpretar correctamente este dataset, se asumen los siguientes supuestos:

1. `IDIOMA = 3` corresponde a inglés.
2. `IDTIPOCURS = 1` corresponde a extensivo de calendario escolar.
3. `NRO_EJERCICIO` entre 10 y 20 equivale a cursos entre 2014-2015 y 2024-2025.
4. `TOTAL <> 0` implica que el alumno tiene resultado final válido.
5. `RESULT <> 0` implica que el alumno ha realizado las partes parciales del examen.
6. `MATERIA` identifica de forma estable cada componente parcial evaluado.
7. La combinación `IDALUMNE + IDCURS + IDEVALUACIO + MATERIA` constituye el identificador único funcional del dataset.
8. La combinación de joins utilizada preserva la relación correcta entre alumno, curso, evaluación y materia.

Estos supuestos deben validarse formalmente para convertir el dataset en una fuente analítica certificada.

---

## 13. Limitaciones del dataset

Este dataset presenta las siguientes limitaciones:

- no incluye otros idiomas distintos de inglés,
- no incluye otras tipologías de curso distintas del extensivo de calendario escolar,
- puede excluir alumnado sin resultado registrado o sin relación completa en todas las tablas,
- puede no representar adecuadamente casos excepcionales si el valor 0 tiene semántica ambigua,
- el resultado total puede estar repetido en varias filas al estar el dataset a nivel de materia,
- y puede requerir depuración adicional para asegurar unicidad y consistencia de valores categóricos.

---

## 14. Recomendaciones para la fase de análisis

Antes de iniciar el análisis posterior, se recomienda:

- validar el diccionario de datos de todos los campos seleccionados, especialmente `MATERIA`,
- verificar la unicidad de la clave compuesta `IDALUMNE + IDCURS + IDEVALUACIO + MATERIA`,
- cuantificar nulos, duplicados y outliers,
- comprobar que los filtros no eliminan población relevante,
- separar conceptualmente los análisis a nivel de **materia** y a nivel de **evaluación**,
- deduplicar o reagrupar cuando se utilice `TOTAL`,
- derivar variables analíticas útiles como edad, curso académico normalizado o segmentos geográficos,
- y documentar cualquier transformación adicional realizada sobre el dataset base.

---

## 15. Conclusión ejecutiva

El dataset generado constituye una base sólida para el análisis del rendimiento en exámenes de inglés, al integrar información académica, demográfica y temporal en una única extracción. La incorporación del campo `MATERIA` mejora el nivel de detalle analítico, permitiendo estudiar el rendimiento parcial por componente del examen, pero al mismo tiempo introduce una mayor complejidad en la granularidad del dataset.

En esta versión, la unidad analítica correcta pasa a ser **alumno + curso + evaluación + materia**, lo que obliga a interpretar con cuidado el campo `TOTAL`, ya que puede repetirse en varias filas correspondientes a un mismo examen. Con una validación previa de la clave compuesta, del significado funcional de `MATERIA` y de la semántica de los valores 0, el dataset resulta adecuado para la fase de análisis exploratorio y para la construcción de métricas de rendimiento y segmentación.

import argparse
import pandas as pd
from pathlib import Path
import math
import html
import json
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Carga la configuración desde el archivo .env situado en la raíz del proyecto.
load_dotenv(dotenv_path=BASE_DIR / ".env")

foto_alumne_template = os.getenv("FOTO_ALUMNE")
logo_escola = os.getenv("LOGO_ESCOLA")
pass_mark_raw = os.getenv("PASS_MARK")
model_llm = os.getenv("MODEL_LLM", "nvidia/nemotron-3.5-super-vl:free")


def validate_configuration():
    """Valida la configuración necesaria sin mostrar valores sensibles."""
    missing = [
        name for name, value in (
            ("FOTO_ALUMNE", foto_alumne_template),
            ("LOGO_ESCOLA", logo_escola),
            ("PASS_MARK", pass_mark_raw),
            ("MODEL_LLM", model_llm),
        )
        if value is None or not value.strip()
    ]
    if missing:
        raise SystemExit(
            "Error de configuración: faltan variables en el archivo .env: "
            + ", ".join(missing)
            + ". Revisa .env.example."
        )

    try:
        return float(pass_mark_raw)
    except ValueError as exc:
        raise SystemExit(
            "Error de configuración: la variable PASS_MARK del archivo .env debe ser un número."
        ) from exc


def parse_bool(value):
    value = value.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise argparse.ArgumentTypeError("El valor debe ser true o false.")

# ============================================================
# 1. RECIBIR ARGUMENTOS EXTERNOS
# ============================================================
parser = argparse.ArgumentParser(
    description="Analiza los resultados de un alumno."
)

parser.add_argument(
    "--idalumne",
    type=int,
    required=True,
    help="ID del alumno"
)

parser.add_argument(
    "--data",
    required=True,
    help="Fecha de la evaluación en formato YYYY-MM-DD"
)


parser.add_argument(
    "--language",
    type=str,
    choices=["ca", "es", "en"],
    default="ca",
    help="Idioma del informe según ISO 639-1: ca (catalán), es (castellano), en (inglés)"
)

parser.add_argument(
    "--analisis-ia",
    type=parse_bool,
    default=True,
    metavar="{true,false}",
    help="Activa o desactiva el análisis con IA (por defecto: true)"
)

args = parser.parse_args()

PASS_MARK = validate_configuration()

id_alumne = args.idalumne
data_avaluacio = args.data
language_code = args.language
language = {"ca": "catala", "es": "castellano", "en": "english"}[language_code]
analisis_ia_activada = args.analisis_ia

#id_alumne = "1690"
#data_avaluacio = "2026-06-20"

# ============================================================
# 2. CARGAR EL ARCHIVO CSV
# ============================================================

ruta_csv = BASE_DIR / "data" / "NOTA_PARCIAL_PONDERADA_ALUMN.csv"

# Comprobar que existe el archivo principal
if not Path(ruta_csv).is_file():
    raise FileNotFoundError(
        f"No se ha encontrado el archivo principal: {ruta_csv}"
    )

df = pd.read_csv(
    ruta_csv,
    sep=";",
    encoding="utf-8-sig",   # Ahora funciona sin engine="python"
    decimal=",",
)


# ============================================================
# 3. NORMALIZAR TIPOS DE DATOS
# ============================================================

df["IDALUMNE"] = df["IDALUMNE"].astype(str).str.strip()

# MATERIA en mayúsculas y sin espacios
df["MATERIA"] = df["MATERIA"].astype(str).str.strip().str.upper()

# DATA com a datetime sense hora
df["DATA"] = pd.to_datetime(
    df["DATA"],
    errors="coerce",
    dayfirst=True
).dt.normalize()

# Convertir también la fecha recibida como argumento
data_avaluacio = pd.to_datetime(
    data_avaluacio,
    dayfirst=True
).normalize()

id_alumne_str = str(id_alumne).strip()


# ============================================================
# 4. FILTRAR POR IDALUMNE Y FECHA
# ============================================================

df = df[
    (df["IDALUMNE"] == id_alumne_str) &
    (df["DATA"] == data_avaluacio)
].copy()

print(f"Registros encontrados: {len(df)}")

if df.empty:
    raise SystemExit(
        f"⚠️ No hay registros para IDALUMNE={id_alumne_str} y DATA={data_avaluacio.date()}"
    )

# Guardar el identificador de la evaluación para utilizarlo después al generar el informe HTML
id_avaluacio = int(df["IDEVALUACIO"].iloc[0])
# Guardar el identificador del curso para utilizarlo después al generar el informe HTML
id_curs=df["IDCURS"].iloc[0]

# ============================================================
# 5. COMPETENCIAS QUE QUEREMOS ANALIZAR
# ============================================================

materies = [
    "GRAMMAR",
    "LISTENING",
    "READING",
    "SPEAKING",
    "WRITING"
]


# ============================================================
# 6. CREAR DF_ANALISIS
# ============================================================

df_analisis = (
    df.set_index("MATERIA")["PERCENTATGE"]
    .reindex(materies)      # Fuerza el orden de las cinco competencias
    .to_frame()
    .T
)

df_analisis.columns.name = None


# ============================================================
# 7. AÑADIR IDALUMNE Y FECHA
# ============================================================

df_analisis.insert(
    0,
    "IDALUMNE",
    id_alumne
)

df_analisis.insert(
    1,
    "DATA",
    data_avaluacio
)

df_analisis.insert(
    2,
    "IDEVALUACIO",
    id_avaluacio
)

df_analisis.insert(
    3,
    "IDCURS",
    id_curs
)


# ============================================================
# 8. CALCULAR LA MEDIA
# ============================================================

df_analisis["Average"] = (
    df_analisis[materies].mean(axis=1)
)


# ============================================================
# 9. MEJOR COMPETENCIA
# ============================================================

df_analisis["Best"] = (
    df_analisis[materies].idxmax(axis=1)
)


# ============================================================
# 10. PEOR COMPETENCIA
# ============================================================

df_analisis["Worst"] = (
    df_analisis[materies].idxmin(axis=1)
)


# ============================================================
# 11. RANGE
# ============================================================

df_analisis["RANG"] = (
    df_analisis[materies].max(axis=1)
    -
    df_analisis[materies].min(axis=1)
)


# ============================================================
# 12. ORDENAR LAS COLUMNAS
# ============================================================

df_analisis = df_analisis[
    [
        "IDALUMNE",
        "DATA",
        "IDEVALUACIO",
        "IDCURS",
        "GRAMMAR",
        "LISTENING",
        "READING",
        "SPEAKING",
        "WRITING",
        "Average",
        "Best",
        "Worst",
        "RANG"
    ]
]


# ============================================================
# 13. MOSTRAR RESULTADOS
# ============================================================

print("\nResultados del alumno:")
print(df)

print("\nPerfil del alumno:")
print(df_analisis)


# ============================================================
# 14. CREAR EL PERFIL DEL ALUMNO PARA EL LLM
# ============================================================

# Obtener la primera fila del DataFrame de análisis
fila = df_analisis.iloc[0]

student_profile = {
    "student_id": int(fila["IDALUMNE"]),
    "evaluation_date": fila["DATA"].strftime("%Y-%m-%d"),

    "skills": {
        "grammar": float(fila["GRAMMAR"]),
        "listening": float(fila["LISTENING"]),
        "reading": float(fila["READING"]),
        "speaking": float(fila["SPEAKING"]),
        "writing": float(fila["WRITING"])
    },

    "average": round(float(fila["Average"]), 2),
    "best_skill": str(fila["Best"]).lower(),
    "weakest_skill": str(fila["Worst"]).lower(),
    "range": round(float(fila["RANG"]), 2)
}

print("\nPerfil preparado para el LLM:")
print(student_profile)


import json


# ============================================================
# 15. CONTEXTO ESTADÍSTICO Y PEDAGÓGICO
# ============================================================

context_estadistic = """
CONTEXT FOR THE ANALYSIS OF ENGLISH LANGUAGE RESULTS

The data are derived from an analysis of student results
in extensive English courses.

The five competencies assessed are:
- Reading
- Grammar
- Writing
- Listening
- Speaking

1. WEIGHTING OF COMPETENCIES

According to the calculation formula for the TOTAL,
each competency accounts for 20% of the final grade.

TOTAL = (READING + GRAMMAR + WRITING + LISTENING + SPEAKING) / 5

All five competencies carry the same mathematical weight.
A competency should not be considered to have a greater weight
in the final grade simply because it shows a higher
correlation with the TOTAL.

2. CORRELATION BETWEEN EACH COMPETENCY AND THE TOTAL

- Grammar: 0.803
- Listening: 0.713
- Reading: 0.709
- Writing: 0.509
- Speaking: 0.496

These correlations describe the relationship observed within
the analyzed population. They do not demonstrate causality,
nor do they, on their own, determine an individual student's level.

3. CORRELATION BETWEEN COMPETENCIES

- Grammar - Listening: 0.458
- Writing - Speaking: 0.454
- Reading - Grammar: 0.392
- Grammar - Writing: 0.344
- Reading - Listening: 0.259
- Reading - Speaking: 0.250
- Listening - Speaking: 0.211
- Reading - Writing: 0.225
- Listening - Writing: 0.175

The observed correlations are weak to moderate. Therefore, it should not be assumed that improving one
competency automatically leads to the improvement of another.

4. RESULTS OF THE MULTIPLE LINEAR REGRESSION

In the analysis provided, the regression reproduces the
formula for the TOTAL, with coefficients of 0.2 for each
competency, an intercept of 0, and an R² = 1.

These results are consistent with a deterministic
relationship, given that the TOTAL is calculated
precisely as the average of the five competencies.

While this regression validates the mathematical formula
for the TOTAL, it does not demonstrate that improving
one competency causes improvements in the others, nor
does it show that any specific pedagogical strategy is
more effective than another.

5. PEDAGOGICAL INTERPRETATION

Grammar shows the highest correlation with the TOTAL
within the studied population.

Writing and Speaking show lower correlations with the
TOTAL, as well as a moderate correlation with each
other. This may justify exploring specific needs
regarding written and oral expression, though it does
not imply that these are always the priorities for every
individual student.

Individual priorities should be determined based on
scores from a student's specific profile, the full set of
five competencies, and their learning objectives.

One should not invent statistical conclusions or attribute
results to the study that are not actually present in it.
"""


# ============================================================
# 16. INSTRUCCIONES PARA EL LLM
# ============================================================


instruccions_llm = """
ROLE

Act as a pedagogical analysis assistant specialized
in English language learning and assessment.

Your goal is to help the student understand their results,
recognize their strengths, and identify practical ways
to improve their English.

TASKS

1. Identify the student's strengths.
2. Identify the skills that need improvement.
3. Interpret the balance across the five skills.
4. Propose between 2 and 4 specific learning activities.

For each proposed activity, provide:
- The skill being addressed.
- A clear description.
- Step-by-step procedure.
- A specific learning objective.

TONE AND COMMUNICATION STYLE

- Address the student directly in the second person singular,
  as if speaking to them personally.
- Use an informal, friendly, warm, encouraging,
  and conversational tone.
- Speak to the student as you would to a student you know
  well or a trusted classmate.
- Use clear, natural, everyday language.
- Be respectful, supportive, and honest.
- Avoid formal forms of address, honorifics,
  and impersonal third-person descriptions of the student.
- Never address the student using formal equivalents
  of "you", such as "usted" in Spanish.
- In Catalan, use the informal "tu" form.
- In Spanish, use the informal "tú" form.
- In English, speak directly to the student using "you".
- Prefer expressions such as "You are doing really well
  at...", "Et surt molt bé...", or "Se't dona bé..."
  instead of detached expressions such as
  "The student demonstrates proficiency in...".
- Explain areas for improvement positively and constructively.
  Focus on what the student can practise and how they can improve.
- Avoid sounding robotic, excessively academic,
  judgmental, cold, or overly formal.
- Do not exaggerate praise or make promises about results.
- Maintain this tone consistently throughout the entire report,
  including observations, skills balance, and activities.

PEDAGOGICAL CRITERIA

- Base individual priorities on the student's actual scores.
- Consider all five skills equally: each contributes 20%
  to the final score.
- Do not confuse correlation with causation.
- Do not assume that improving one skill will
  automatically improve another.
- Do not invent scores, age, proficiency level,
  or CEFR level.
- Distinguish observed results from pedagogical hypotheses.
- Suggest practical activities that can be implemented
  in an English course.
- Return valid JSON only, following the required schema.
- Address the student directly in the informal second person.
  Never describe the student as "the student" when you can
  naturally speak to them as "you".
"""





# ============================================================
# ESQUEMA JSON OBLIGATORIO PARA LA RESPUESTA DEL LLM
# ============================================================

esquema_json = """
Retorna exclusivament un objecte JSON vàlid amb EXACTAMENT
les cinc claus principals següents:

{
  "student_data": {
    "student_id": 0,
    "evaluation_date": "YYYY-MM-DD",
    "skills": {
      "grammar": 0.0,
      "listening": 0.0,
      "reading": 0.0,
      "speaking": 0.0,
      "writing": 0.0
    },
    "average": 0.0,
    "best_skill": "grammar",
    "weakest_skill": "grammar",
    "range": 0.0
  },
  "strengths": [
    {
      "skill": "reading",
      "score": 0.0,
      "observation": "string"
    }
  ],
  "areas_to_improve": [
    {
      "skill": "grammar",
      "score": 0.0,
      "priority": "High",
      "observation": "string"
    }
  ],
  "skills_balance": "string",
  "proposed_activities": [
    {
      "skill": "grammar",
      "description": "string",
      "procedure": "string",
      "learning_objective": "string"
    }
  ]
}

INSTRUCCIONES OBLIGATORIAS:

1. The `student_data` section must exactly replicate
   the data from the individual profile provided in the prompt.
   Do not invent or recalculate different values.

2. Keep `student_id` and `evaluation_date` within `student_data`.

3. The five competencies must retain their original scores.

4. All JSON keys must strictly maintain
   the English names defined in this schema.

5. The competency names must always be:
   `grammar`, `listening`, `reading`, `speaking`, and `writing`.

6. The `priority` values ​​must be exclusively:
   `High`, `Medium`, or `Low`.
   Do not translate these values.

7. The textual content of the report must be in the
   selected language: Catalan, Spanish, or English.

8. Translate explanatory texts, observations,
   descriptions, procedures, and learning objectives,
   but do not translate JSON keys,
   competency names, or `priority` values.

9. The `strengths`, `areas_to_improve`, and
   `proposed_activities` sections must be lists of objects.

10. `skills_balance` must be a text string.

11. Do not confuse correlation with causation. All five
    competencies contribute 20% each to the final score.
    Base individual priorities on the student's scores.

12. Do not add keys, comments, Markdown, or explanations
    outside the JSON object.
"""


# ============================================================
# 17. CONSTRUIR EL PROMPT COMPLETO PARA EL LLM
# ============================================================


import json

perfil_json = json.dumps(
    student_profile,
    ensure_ascii=False,
    indent=2
)

prompt_llm = f"""
{instruccions_llm}

CONTEXTO ESTADISTICO:
{context_estadistic}

PERFIL INDIVIDUAL DE ALUMNO:
{perfil_json}

ESQUEMA JSON OBLIGATORIO:
{esquema_json}

FINAL OUTPUT INSTRUCTIONS

1. Write all pedagogical text in the selected language:
   {language}

2. The selected language applies to observations,
   skills balance, activity descriptions, procedures,
   and learning objectives.

3. Keep every JSON key exactly as defined in the schema.
   All JSON keys must remain in English.

4. Keep skill identifiers unchanged:
   grammar, listening, reading, speaking, writing.

5. The priority field must contain only:
   High, Medium, or Low.

6. Copy the student profile into student_data exactly.
   Do not modify or recalculate any profile values.

7. Return exactly one valid JSON object.
   Do not include Markdown, comments, or explanations
   outside the JSON object.
"""

# ============================================================
# 18. MOSTRAR EL PROMPT PARA COMPROBARLO
# ============================================================

print("\\nPROMPT PREPARAT PER AL LLM:\\n")
print(prompt_llm)


# ============================================================
# 19. LLAMAR AL LLM Y CONSERVAR EL JSON EN MEMORIA (OPCIONAL)
# ============================================================

informe = None

if analisis_ia_activada:
    # Validar la clave antes de importar el cliente o intentar conectar.
    api_key = os.getenv("MODEL_API_KEY")
    if not api_key or not api_key.strip():
        raise SystemExit(
            "Error de configuración: falta MODEL_API_KEY en el archivo .env "
            "o en las variables de entorno. No se ha mostrado ninguna credencial."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit(
            "Falta la dependència 'openai'. Instal·la-la amb: pip install -r requirements.txt"
        ) from exc

    # Connectar amb OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    try:
        completion = client.chat.completions.create(
            model=model_llm,
            messages=[
                {
                    "role": "user",
                    "content": prompt_llm
                }
            ],
            extra_body={
                "reasoning": {"enabled": True}
            }
        )

        resposta = completion.choices[0].message.content

        if not resposta:
            raise ValueError("El model no ha retornat cap resposta.")

        informe = json.loads(resposta)

        # El JSON es conserva únicament en memòria per a la validació
        # y la generación del HTML. No se crea ningún archivo ni carpeta JSON.
        print("Informe JSON generado en memoria (sin guardar ningún archivo).")

    except json.JSONDecodeError as exc:
        raise ValueError(
            "El model no ha retornat un JSON vàlid."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Error al generar el informe con IA: {exc}") from exc
else:
    print("Análisis con IA desactivado: no se realizará ninguna llamada al LLM ni se generará JSON pedagógico.")

if analisis_ia_activada:
    # ============================================================
    # 20. VALIDAR LAS CLAVES PRINCIPALES DEL JSON
    # ============================================================

    claus_obligatories = {
        "student_data",
        "strengths",
        "areas_to_improve",
        "skills_balance",
        "proposed_activities"
    }

    if not isinstance(informe, dict):
        raise ValueError("El informe no es un objeto JSON.")

    claus_faltants = claus_obligatories - set(informe.keys())

    if claus_faltants:
        raise ValueError(
            f"Falten llaves obligatorias: {claus_faltants}"
        )

    if not isinstance(informe["student_data"], dict):
        raise ValueError("'student_data' debe ser un objeto.")

    if not isinstance(informe["strengths"], list):
        raise ValueError("'strengths' debe ser una lista.")

    if not isinstance(informe["areas_to_improve"], list):
        raise ValueError(
            "'areas_to_improve' ha de ser una lista."
        )

    if not isinstance(informe["skills_balance"], str):
        raise ValueError("'skills_balance' debe ser texto.")

    if not isinstance(informe["proposed_activities"], list):
        raise ValueError(
            "'proposed_activities' ha de ser una lista."
        )


    # Informar que la validación ha estado correcta
    print("Estructura básica del JSON validada correctamente.")



    # ============================================================
    # 21. VALIDAR LA COHERENCIA PEDAGÓGICA DEL INFORME
    # ============================================================

    import math

    # ------------------------------------------------------------
    # 21.1. Comprobar que el perfil devuelto coincida con el original
    # ------------------------------------------------------------

    perfil_retornat = informe["student_data"]

    camps_exactes = [
        "student_id",
        "evaluation_date",
        "best_skill",
        "weakest_skill"
    ]

    for camp in camps_exactes:
        if perfil_retornat.get(camp) != student_profile.get(camp):
            raise ValueError(
                f"Error en student_data: el camp '{camp}' "
                "no coincideix amb el perfil original."
            )

    camps_numerics = ["average", "range"]

    for camp in camps_numerics:
        valor_original = float(student_profile[camp])
        valor_retornat = float(perfil_retornat[camp])

        if not math.isclose(
            valor_original,
            valor_retornat,
            abs_tol=0.01
        ):
            raise ValueError(
                f"Error en student_data: el camp '{camp}' "
                "no coincideix amb el perfil original."
            )

    # Comprobar las cinco notas originales
    for skill, nota_original in student_profile["skills"].items():
        nota_retornada = perfil_retornat["skills"].get(skill)

        if nota_retornada is None or not math.isclose(
            float(nota_original),
            float(nota_retornada),
            abs_tol=0.01
        ):
            raise ValueError(
                f"Error: la nota de '{skill}' "
                "no coincideix amb el perfil original."
            )

    # ------------------------------------------------------------
    # 21.2. Comprobar que las competencias sean válidas
    # ------------------------------------------------------------

    competencies_valides = {
        "grammar",
        "listening",
        "reading",
        "speaking",
        "writing"
    }

    mitjana = float(student_profile["average"])
    notes = student_profile["skills"]

    avisos_pedagogics = []

    # ------------------------------------------------------------
    # 21.3. Revisar los puntos fuertes
    # ------------------------------------------------------------

    for punt in informe["strengths"]:
        skill = punt["skill"]

        if skill not in competencies_valides:
            raise ValueError(
                f"Competencia no válida a strengths: {skill}"
            )

        nota_real = float(notes[skill])
        nota_informe = float(punt["score"])

        if not math.isclose(nota_real, nota_informe, abs_tol=0.01):
            raise ValueError(
                f"La nota de '{skill}' a strengths "
                "no coincide con las datos originales."
            )

        if nota_real < mitjana:
            avisos_pedagogics.append(
                f"Revisa si '{skill}' es realmente una fortalesa: "
                f"su nota ({nota_real}) es inferior "
                f"a la media ({mitjana})."
            )

    # ------------------------------------------------------------
    # 21.4. Revisar las competencias que deben reforzarse
    # ------------------------------------------------------------

    prioritats_valides = {"High", "Medium", "Low"}

    for area in informe["areas_to_improve"]:
        skill = area["skill"]

        if skill not in competencies_valides:
            raise ValueError(
                f"Competencia no válida a areas_to_improve: {skill}"
            )

        nota_real = float(notes[skill])
        nota_informe = float(area["score"])

        if not math.isclose(nota_real, nota_informe, abs_tol=0.01):
            raise ValueError(
                f"La nota de '{skill}' a areas_to_improve "
                "no coincide con las datos originales."
            )

        if area["priority"] not in prioritats_valides:
            raise ValueError(
                f"Prioritat no válida per a '{skill}': "
                f"{area['priority']}"
            )

        if nota_real >= mitjana:
            avisos_pedagogics.append(
                f"Revisa si cal reforçar '{skill}': "
                f"la seva nota ({nota_real}) no és inferior "
                f"a la mitjana ({mitjana})."
            )

    # ------------------------------------------------------------
    # 21.5. Comprobar las actividades proposadas
    # ------------------------------------------------------------

    if not 2 <= len(informe["proposed_activities"]) <= 4:
        raise ValueError(
            "El informe ha de contener entre 2 i 4 actividades."
        )

    for activitat in informe["proposed_activities"]:
        skill = activitat["skill"]

        if skill not in competencies_valides:
            raise ValueError(
                f"Competencia no válida en una actividad: {skill}"
            )

        if not any(
            area["skill"] == skill
            for area in informe["areas_to_improve"]
        ):
            avisos_pedagogics.append(
                f"La actividad sobre '{skill}' no está asociada "
                "a ninguna competencia de areas_to_improve. "
                "Revisa si la propuesta está justificada."
            )

    # ------------------------------------------------------------
    # 21.6. Mostrar los avisos pedagógicos
    # ------------------------------------------------------------

    if avisos_pedagogics:
        print("\nAVISOS DE COHERENCIA PEDAGÓGICA:")

        for avís in avisos_pedagogics:
            print(f"- {avís}")
    else:
        print(
            "Validación pedagógica superada: "
            "no se han detectado incoherencias básicas."
        )






# ============================================================
# 22. GENERAR EL INFORME HTML COMPLETO
# ============================================================

import html
import math
from pathlib import Path


def generar_informe_html(
    informe,
    language,
    info_extra=None,
    carpeta_sortida="reports",
    ruta_css="style.css",
    include_ai_analysis=True
):
    """
    Genera un informe HTML con:
      1. Cabecera de la evaluación.
      2. Resultados académicos y gráficos circulares.
      3. Informe pedagógico generado por la LLM.
      4. Comentario original del profesor.

    Los textos del informe se escapan para evitar que datos
    externas se interpreten como código HTML.
    """

    # --------------------------------------------------------
    # 1. IDIOMA Y TEXTOS DE LA INTERFAZ
    # --------------------------------------------------------

    textos = {
        "catala": {
            "title": "Informe de rendiment acadèmic",
            "subtitle": "Informe individual d'aprenentatge d'anglès",
            "student": "Alumne/a",
            "course": "Curs",
            "teacher": "Professor/a",
            "evaluation": "Avaluació",
            "school_year": "Any escolar",
            "student_id": "Identificador de l'alumne",
            "evaluation_date": "Data de l'avaluació",
            "results": "Resultats acadèmics",
            "average": "Mitjana",
            "result_final": "Resultat final",
            "pass_mark": "Llindar de superació",
            "skills": "Resultats per competència",
            "best": "Millor competència",
            "weakest": "Competència a reforçar",
            "strengths": "Punts forts",
            "improvements": "Aspectes a millorar",
            "priority": "Prioritat",
            "balance": "Equilibri entre competències",
            "activities": "Propostes d'activitats",
            "description": "Descripció",
            "procedure": "Com ho pots practicar",
            "objective": "Objectiu d'aprenentatge",
            "teacher_comment": "Comentari del professor",
            "teacher_comment_intro":
                "Observacions originals del professor sobre l'avaluació.",
            "ai_label": "Anàlisi pedagògica assistida per IA",
            "teacher_label": "Valoració del professor",
            "score": "Puntuació",
            "print": "Imprimir / Desar com a PDF",
            "footer": "Informe individual de seguiment acadèmic",
            "no_comment": "No hi ha cap comentari del professor registrat.",
            "no_data": "Informació no disponible",
            "no_strengths": "No s'han registrat punts forts.",
            "no_improvements": "No s'han registrat aspectes a millorar.",
            "no_activities": "No s'han proposat activitats.",
            "high": "Alta",
            "medium": "Mitjana",
            "low": "Baixa",
            "grammar": "Grammar",
            "listening": "Listening",
            "reading": "Reading",
            "speaking": "Speaking",
            "writing": "Writing",
        },

        "castellano": {
            "title": "Informe de rendimiento académico",
            "subtitle": "Informe individual de aprendizaje de inglés",
            "student": "Alumno/a",
            "course": "Curso",
            "teacher": "Profesor/a",
            "evaluation": "Evaluación",
            "school_year": "Año escolar",
            "student_id": "Identificador del alumno",
            "evaluation_date": "Fecha de evaluación",
            "results": "Resultados académicos",
            "average": "Media",
            "result_final": "Resultado final",
            "pass_mark": "Nota de aprobado",
            "skills": "Resultados por competencia",
            "best": "Mejor competencia",
            "weakest": "Competencia a reforzar",
            "strengths": "Puntos fuertes",
            "improvements": "Aspectos a mejorar",
            "priority": "Prioridad",
            "balance": "Equilibrio entre competencias",
            "activities": "Propuestas de actividades",
            "description": "Descripción",
            "procedure": "Cómo puedes practicarlo",
            "objective": "Objetivo de aprendizaje",
            "teacher_comment": "Comentario del profesor",
            "teacher_comment_intro":
                "Observaciones originales del profesor sobre la evaluación.",
            "ai_label": "Análisis pedagógico asistido por IA",
            "teacher_label": "Valoración del profesor",
            "score": "Puntuación",
            "print": "Imprimir / Guardar como PDF",
            "footer": "Informe individual de seguimiento académico",
            "no_comment": "No hay ningún comentario del profesor registrado.",
            "no_data": "Información no disponible",
            "no_strengths": "No se han registrado puntos fuertes.",
            "no_improvements": "No se han registrado aspectos a mejorar.",
            "no_activities": "No se han propuesto actividades.",
            "high": "Alta",
            "medium": "Media",
            "low": "Baja",
            "grammar": "Grammar",
            "listening": "Listening",
            "reading": "Reading",
            "speaking": "Speaking",
            "writing": "Writing",
        },

        "english": {
            "title": "Academic Performance Report",
            "subtitle": "Individual English Learning Report",
            "student": "Student",
            "course": "Course",
            "teacher": "Teacher",
            "evaluation": "Assessment",
            "school_year": "Academic year",
            "student_id": "Student ID",
            "evaluation_date": "Assessment date",
            "results": "Academic results",
            "average": "Average",
            "result_final": "Final result",
            "pass_mark": "Pass mark",
            "skills": "Results by skill",
            "best": "Strongest skill",
            "weakest": "Skill to develop",
            "strengths": "Strengths",
            "improvements": "Areas to improve",
            "priority": "Priority",
            "balance": "Balance across skills",
            "activities": "Suggested activities",
            "description": "Description",
            "procedure": "How to practise",
            "objective": "Learning objective",
            "teacher_comment": "Teacher's comment",
            "teacher_comment_intro":
                "Original teacher observations about the assessment.",
            "ai_label": "AI-assisted pedagogical analysis",
            "teacher_label": "Teacher's assessment",
            "score": "Score",
            "print": "Print / Save as PDF",
            "footer": "Individual academic progress report",
            "no_comment": "No teacher comment has been recorded.",
            "no_data": "Information not available",
            "no_strengths": "No strengths have been recorded.",
            "no_improvements": "No areas for improvement have been recorded.",
            "no_activities": "No activities have been suggested.",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "grammar": "Grammar",
            "listening": "Listening",
            "reading": "Reading",
            "speaking": "Speaking",
            "writing": "Writing",
        }
    }

    if language not in textos:
        raise ValueError(
            f"Idioma no válido: {language}. "
            "Utiliza catala, castellano o english."
        )

    t = textos[language]

    # --------------------------------------------------------
    # 2. DATOS DEL INFORME I FUNCIONES AUXILIARES
    # --------------------------------------------------------

    informe = informe or {}
    dades = informe.get("student_data", {})
    notes = dades.get("skills", {})
    info_extra = info_extra or {}
    mostra_analisi_ia = bool(include_ai_analysis and informe)

    def esc(valor):
        """Escapa texto para insertarlo con seguridad en el HTML."""
        if valor is None:
            return ""
        if isinstance(valor, float) and math.isnan(valor):
            return ""
        return html.escape(str(valor).strip())

    def valor_extra(clau):
        valor = info_extra.get(clau)
        resultat = esc(valor)
        return resultat if resultat else esc(t["no_data"])

    def numero(valor):
        """Convierte una puntuación a float de manera segura."""
        try:
            resultat = float(valor)
            if not math.isfinite(resultat):
                return 0.0
            return max(0.0, min(100.0, resultat))
        except (TypeError, ValueError):
            return 0.0

    def format_nota(valor):
        return f"{numero(valor):.2f}".rstrip("0").rstrip(".")

    def text_skill(skill):
        return esc(t.get(skill, skill.capitalize()))

    # Los datos del LLM no deben contener HTML ejecutable.
    # esc() s'aplica a tots els textos dinàmics que es mostren.

    student_id = esc(dades["student_id"])
    evaluation_date = esc(dades.get("evaluation_date", ""))
    try:
        data_avaluacio_formatada = pd.to_datetime(
            dades.get("evaluation_date"), errors="raise"
        ).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        data_avaluacio_formatada = evaluation_date

    # Las rutas visuales se configuran mediante variables del archivo .env.
    foto_alumne = foto_alumne_template.format(student_id=student_id)

    # --------------------------------------------------------
    # 3. GRÁFICOS CIRCULARES DE PROGRESO
    # --------------------------------------------------------

    def generar_grafic_circular(etiqueta, valor, classe=""):
        """
        Gráfico circular de progreso de 0 a 100.
        Utilitza CSS conic-gradient, sin dependencias externas.
        """

        puntuacio = numero(valor)
        angle = puntuacio * 3.6

        return f"""
        <div class="score-card {classe}">
            <div
                class="donut-chart"
                role="img"
                aria-label="{esc(etiqueta)}: {format_nota(puntuacio)}%"
                style="--score-angle: {angle:.2f}deg;"
            >
                <div class="donut-inner">
                    <span class="donut-value">
                        {format_nota(puntuacio)}
                    </span>
                    <span class="donut-percent">%</span>
                </div>
            </div>
            <h3>{esc(etiqueta)}</h3>
        </div>
        """

    valor_mitjana_original = dades.get("average")
    try:
        mitjana_original_num = float(valor_mitjana_original)
        mitjana_disponible = math.isfinite(mitjana_original_num)
    except (TypeError, ValueError):
        mitjana_original_num = None
        mitjana_disponible = False

    mitjana = numero(valor_mitjana_original)

    # La nota mínima proviene exclusivamente de la variable PASS_MARK del .env.
    pass_mark = PASS_MARK
    try:
        pass_mark_num = float(pass_mark)
        pass_mark_valid = math.isfinite(pass_mark_num)
    except (TypeError, ValueError):
        pass_mark_num = None
        pass_mark_valid = False

    if not mitjana_disponible or not pass_mark_valid:
        estat_examen = "unavailable"
        text_estat_examen = {
            "catala": "Resultat no disponible",
            "castellano": "Resultado no disponible",
            "english": "Result unavailable",
        }[language]
    elif mitjana_original_num >= pass_mark_num:
        estat_examen = "pass"
        text_estat_examen = "Pass"
    else:
        estat_examen = "no-pass"
        text_estat_examen = "No pass"

    # El titulo del panel canvia, pero es conserva la etiqueta "Mitjana"
    # que aparece debajo del gráfico como pie de la tarjeta.
    titol_resultat_final = t["result_final"]
    grafic_mitjana = generar_grafic_circular(
        t["average"],
        mitjana,
        "average-card"
    )

    competències = [
        "grammar",
        "listening",
        "reading",
        "speaking",
        "writing"
    ]

    grafics_competencies = "".join(
        generar_grafic_circular(
            text_skill(skill),
            notes.get(skill, 0)
        )
        for skill in competències
    )

    # --------------------------------------------------------
    # 4. TABLA DE RESULTADOS ACADÉMICOS
    # --------------------------------------------------------

    # La aplicación trabaja con puntuaciones percentuales normalizadas
    # de 0 a 100. Ambas posiciones se expresan en esta misma escala.
    escala_minima = 0.0
    escala_maxima = 100.0
    amplitud_escala = escala_maxima - escala_minima

    def posicio_barra(valor):
        """Retorna la posición percentual dentro de la escala academica."""
        if amplitud_escala <= 0:
            return 0.0
        valor_limitat = max(escala_minima, min(escala_maxima, float(valor)))
        return ((valor_limitat - escala_minima) / amplitud_escala) * 100.0

    pass_bar_marker = ""
    pass_mark_label = t["pass_mark"] + ": " + t["no_data"]
    if pass_mark_valid:
        posicio_llindar = posicio_barra(pass_mark_num)
        pass_bar_marker = (
            '<span class="pass-threshold-marker" '
            f'style="--marker-position: {posicio_llindar:.4f}%" '
            'aria-hidden="true"></span>'
        )
        pass_mark_label = f"{t['pass_mark']}: {format_nota(pass_mark_num)}"

    score_marker = ""
    if mitjana_disponible:
        posicio_resultat = posicio_barra(mitjana)
        score_marker = (
            '<span class="pass-score-marker" '
            f'style="--marker-position: {posicio_resultat:.4f}%" '
            f'title="Resultat final: {format_nota(mitjana)}%" '
            f'aria-label="Resultat final: {format_nota(mitjana)}%">'
            f'<span class="pass-score-value">{format_nota(mitjana)}%</span>'
            '</span>'
        )

    pass_bar_html = f"""
        <div class="pass-bar-component">
            <div class="pass-bar-horizontal-wrap">
                <div class="pass-bar-scale-labels">
                    <span>{format_nota(escala_minima)}</span>
                    <span>{format_nota(escala_maxima)}</span>
                </div>
                <div class="pass-bar pass-bar-horizontal" role="img"
                     aria-label="Escala de resultats de {format_nota(escala_minima)} a {format_nota(escala_maxima)}. {esc(pass_mark_label)}. {esc(text_estat_examen)}.">
                    {pass_bar_marker}
                    {score_marker}
                </div>
            </div>
            <div class="pass-bar-details">
                <div class="pass-mark-label">{esc(pass_mark_label)}</div>
                <div class="pass-result-label exam-status-{estat_examen}" role="status">
                    {esc(text_estat_examen)}
                </div>
            </div>
        </div>
    """

    files_notes = "".join(
        f"""
        <tr>
            <td>{text_skill(skill)}</td>
            <td class="score-cell">
                {format_nota(notes.get(skill, 0))}%
            </td>
            {f'<td class="pass-status-cell" rowspan="{len(competències)}">{pass_bar_html}</td>' if index == 0 else ''}
        </tr>
        """
        for index, skill in enumerate(competències)
    )

    millor = dades.get("best_skill", "")
    pitjor = dades.get("weakest_skill", "")

    targetes_resum = f"""
    <div class="summary-grid">
        <article class="summary-card">
            <span class="summary-label">{esc(t["average"])}</span>
            <strong class="summary-number">{format_nota(mitjana)}%</strong>
        </article>

        <article class="summary-card summary-best">
            <span class="summary-label">{esc(t["best"])}</span>
            <strong class="summary-text">{text_skill(millor)}</strong>
        </article>

        <article class="summary-card summary-weakest">
            <span class="summary-label">{esc(t["weakest"])}</span>
            <strong class="summary-text">{text_skill(pitjor)}</strong>
        </article>
    </div>
    """

    # --------------------------------------------------------
    # 5. PUNTOS FORTES DEL ALUMNO   
    # --------------------------------------------------------

    strengths = informe.get("strengths", [])

    if strengths:
        html_strengths = "".join(
            f"""
            <article class="pedagogy-card strength-card">
                <div class="skill-badge">{text_skill(item.get("skill", ""))}</div>
                <div class="pedagogy-score">
                    {format_nota(item.get("score", 0))}%
                </div>
                <p>{esc(item.get("observation", ""))}</p>
            </article>
            """
            for item in strengths
        )
    else:
        html_strengths = (
            f'<p class="empty-message">{esc(t["no_strengths"])}</p>'
        )

    # --------------------------------------------------------
    # 6. ASPECTOS A MEJORAR
    # --------------------------------------------------------

    improvements = informe.get("areas_to_improve", [])

    priorities = {
        "High": ("high", "priority-high"),
        "Medium": ("medium", "priority-medium"),
        "Low": ("low", "priority-low"),
    }

    if improvements:
        html_improvements = ""

        for item in improvements:
            priority_original = item.get("priority", "")
            priority_key, priority_class = priorities.get(
                priority_original,
                ("medium", "priority-medium")
            )

            priority_label = t[priority_key]

            html_improvements += f"""
            <article class="pedagogy-card improvement-card">
                <div class="improvement-header">
                    <h3>{text_skill(item.get("skill", ""))}</h3>
                    <span class="priority-badge {priority_class}">
                        {esc(t["priority"])}: {esc(priority_label)}
                    </span>
                </div>
                <div class="pedagogy-score">
                    {format_nota(item.get("score", 0))}%
                </div>
                <p>{esc(item.get("observation", ""))}</p>
            </article>
            """
    else:
        html_improvements = (
            f'<p class="empty-message">{esc(t["no_improvements"])}</p>'
        )

    # --------------------------------------------------------
    # 7. EQUILIBRIO ENTRE COMPETENCIAS
    # --------------------------------------------------------

    skills_balance = esc(informe.get("skills_balance", ""))

    # --------------------------------------------------------
    # 8. ACTIVITADES PROPUESTAS POR LA LLM
    # --------------------------------------------------------

    activities = informe.get("proposed_activities", [])

    if activities:
        html_activities = ""

        for index, activitat in enumerate(activities, start=1):
            html_activities += f"""
            <article class="activity-card">
                <div class="activity-number">{index}</div>
                <div class="activity-content">
                    <span class="skill-badge">
                        {text_skill(activitat.get("skill", ""))}
                    </span>

                    <h3>{esc(activitat.get("description", ""))}</h3>

                    <div class="activity-field">
                        <h4>{esc(t["procedure"])}</h4>
                        <p>{esc(activitat.get("procedure", ""))}</p>
                    </div>

                    <div class="activity-objective">
                        <h4>{esc(t["objective"])}</h4>
                        <p>{esc(activitat.get("learning_objective", ""))}</p>
                    </div>
                </div>
            </article>
            """

    else:
        html_activities = (
            f'<p class="empty-message">{esc(t["no_activities"])}</p>'
        )

    # --------------------------------------------------------
    # 9. COMENTARIO ORIGINAL DEL PROFESOR
    # --------------------------------------------------------

    comentari = esc(info_extra.get("teacher_comment"))

    if not comentari:
        comentari = esc(t["no_comment"])

    # --------------------------------------------------------
    # 10. CONSTRUIR EL DOCUMENTO HTML
    # --------------------------------------------------------

    html_lang = language_code

    seccio_analisi_ia = ""
    if mostra_analisi_ia:
        seccio_analisi_ia = f"""
        <!-- ==================================================
             BLOC 3. INFORME PEDAGOGICO GENERADO POR LA LLM
             ================================================== -->

        <section class="report-section">
            <div class="section-header">
                <h2>{esc(t["ai_label"])}</h2>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["strengths"])}</h3>
                <div class="pedagogy-grid strengths-grid" style="grid-template-columns: repeat({max(len(strengths), 1)}, minmax(0, 1fr));">
                    {html_strengths}
                </div>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["improvements"])}</h3>
                <div class="pedagogy-grid improvements-grid" style="grid-template-columns: repeat({max(len(improvements), 1)}, minmax(0, 1fr));">
                    {html_improvements}
                </div>
            </div>

            <div class="balance-card">
                <h3>{esc(t["balance"])}</h3>
                <p>{skills_balance}</p>
            </div>

            <div class="pedagogy-section">
                <h3>{esc(t["activities"])}</h3>
                <div class="activities-list">
                    {html_activities}
                </div>
            </div>
        </section>
        """

    document_html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{esc(t["title"])} - {student_id}</title>

    <link rel="stylesheet" href="informe.css">
</head>

<body class="student-report">

    <div class="report-toolbar no-print">
        <button class="btn btn-primary" onclick="window.print()">
            {esc(t["print"])}
        </button>
    </div>

    <main class="container report-container">

        <!-- ==================================================
             BLOC 1. CABECERA DE LA AVALUACIÓ
             ================================================== -->

        <header class="report-header">
            <div class="header-visual-row">
                <div class="report-brand">
                    <img src="{esc(logo_escola)}"
                         alt="Logo de l'escola"
                         class="school-logo">
                    <span class="brand-text">Comunica-T</span>
                    <span class="brand-subtext">School</span>
                </div>
                <div class="report-heading">
                    <h1>{esc(t["title"])}</h1>
                    <p class="report-subtitle">{esc(t["subtitle"])}</p>
                </div>
                <div class="student-photo-container">
                    <img src="{esc(foto_alumne)}" alt="{esc(t["student"])}" class="student-photo"
                         onerror="this.style.display='none'">
                </div>
            </div>

            <div class="header-info-row academic-info-row">
                <div class="header-info-item">
                    <span>{esc(t["school_year"])}</span>
                    <strong>{valor_extra("school_year")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["course"])}</span>
                    <strong>{valor_extra("course")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["student"])}</span>
                    <strong>{valor_extra("student_name")}</strong>
                </div>
            </div>

            <div class="header-info-row evaluation-info-row">
                <div class="header-info-item">
                    <span>{esc(t["teacher"])}</span>
                    <strong>{valor_extra("teacher")}</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["evaluation"])}</span>
                    <strong>{valor_extra("evaluation_description")} ({data_avaluacio_formatada})</strong>
                </div>
                <div class="header-info-item">
                    <span>{esc(t["student_id"])}</span>
                    <strong>{student_id}</strong>
                </div>
            </div>
        </header>


        <!-- ==================================================
             BLOC 2. RESULTADOS ACADÉMICOS
             ================================================== -->

        <section class="report-section">
            <div class="section-header">
                <h2>{esc(t["results"])}</h2>
            </div>

            {targetes_resum}

            <div class="scores-layout">

                <div class="average-chart-panel">
                    <h3>{esc(titol_resultat_final)}</h3>
                    {grafic_mitjana}
                </div>

                <div class="skills-panel">
                    <h3>{esc(t["skills"])}</h3>

                    <div class="scores-grid">
                        {grafics_competencies}
                    </div>
                </div>

            </div>

            <div class="scores-table-container">
                <table class="scores-table">
                    <thead>
                        <tr>
                            <th>{esc(t["skills"])}</th>
                            <th>{esc(t["score"])}</th>
                            <th class="pass-status-heading">Pass/No pass</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_notes}
                    </tbody>
                </table>
            </div>
        </section>


        {seccio_analisi_ia}

        <!-- ==================================================
             BLOC 4. COMENTARIO DEL PROFESOR
             ================================================== -->

        <section class="report-section teacher-report-section">
            <div class="section-header">
                <h2>{esc(t["teacher_comment"])}</h2>
            </div>

            <div class="teacher-comment-card">
                <div class="teacher-comment-label">
                    {esc(t["teacher_label"])}
                </div>

                <p class="teacher-comment-intro">
                    {esc(t["teacher_comment_intro"])}
                </p>

                <div class="teacher-comment-text">{comentari}</div>

                <div class="teacher-signature">
                    {esc(t["teacher"])}:
                    <strong>{valor_extra("teacher")}</strong>
                </div>
            </div>
        </section>


        <footer class="report-footer">
            <p class="report-footer-caption">{esc(t["footer"])} <span class="footer-separator">|</span> <span class="footer-school-name">Escola Comunica't</span></p>
            <nav class="contact-footer" aria-label="Contacte de l'escola">
                <a href="https://www.google.com/maps/search/?api=1&query=Entença%2C%2089%2C%2008015%2C%20Barcelona" target="_blank" rel="noopener noreferrer">📍 Entença, 89, 08015, Barcelona</a>
                <a href="tel:+34934262479">☎ 934 262 479</a>
                <a href="https://wa.me/34601302029" target="_blank" rel="noopener noreferrer">💬 601 30 20 29</a>
                <a href="mailto:info@comunicat.school">✉ info@comunicat.school</a>
                <a href="https://www.comunicat.school" target="_blank" rel="noopener noreferrer">🌐 www.comunicat.school</a>
            </nav>
        </footer>

    </main>
</body>
</html>
"""

    # --------------------------------------------------------
    # 11. CREAR LA CARPETA DE SALIDA Y LA HOJA DE ESTILOS
    # --------------------------------------------------------

    carpeta = Path(carpeta_sortida)
    if not carpeta.is_absolute():
        carpeta = BASE_DIR / carpeta
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta_css_origen = Path(ruta_css)
    if not ruta_css_origen.is_absolute():
        ruta_css_origen = BASE_DIR / ruta_css_origen

    if not ruta_css_origen.is_file():
        raise FileNotFoundError(
            f"No se ha encontrado la hoja de estilos: {ruta_css_origen}. "
            "Guarda style.css en el directorio del proyecto o indica "
            "la ruta correcta con el parámetro ruta_css."
        )

    # Leer la hoja de estilos corporativa original
    css_original = ruta_css_origen.read_text(encoding="utf-8")

    # Estilos adicionales específicos del informe
    css_informe = r"""
/* ==========================================================
   INFORME ACADEMICO - ESTILOS ADDICIONALES
   Se conserven los estilos corporativos de style.css.
   ========================================================== */

:root {
    --highlight-yellow: #f4d800;
}

.student-report {
    background: var(--gray-50);
    color: var(--gray-700);
    padding: 24px 0;
}

.report-container {
    background: var(--white);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    padding-top: 32px;
    padding-bottom: 32px;
}

.report-toolbar {
    max-width: 1200px;
    margin: 0 auto 16px;
    padding: 0 24px;
    display: flex;
    justify-content: flex-end;
}

.report-header {
    display: grid;
    grid-template-columns: minmax(100px, 160px) 1fr 120px;
    align-items: center;
    gap: 20px;
    padding-bottom: 28px;
    border-bottom: 3px solid var(--primary-blue);
}

.report-brand {
    grid-column: 1;
    grid-row: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    width: 100%;
    min-width: 0;
    white-space: nowrap;
    line-height: 1.05;
}

.school-logo {
    display: block;
    width: 100%;
    max-width: 160px;
    max-height: 90px;
    height: 90px;
    object-fit: contain;
    object-position: left center;
}

.brand-text {
    display: block;
    max-width: 100%;
    margin-top: 5px;
    font-family: var(--font-primary);
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--primary-blue-dark);
    background: none;
    background-clip: border-box;
    -webkit-background-clip: border-box;
    -webkit-text-fill-color: var(--primary-blue-dark);
    white-space: nowrap;
}

.brand-subtext {
    display: block;
    margin-top: 2px;
    font-family: var(--font-secondary);
    font-size: .85rem;
    font-weight: 600;
    letter-spacing: .12em;
    color: var(--gray-600);
    white-space: nowrap;
}

.report-heading {
    grid-column: 2;
    grid-row: 1;
    text-align: center;
}

.report-heading h1 {
    font-size: clamp(1.5rem, 3vw, 2.3rem);
    margin-bottom: 8px;
}

.report-subtitle {
    color: var(--gray-600);
}

.student-photo-container {
    grid-column: 3;
    grid-row: 1;
    justify-self: end;
}

.student-photo {
    width: 110px;
    height: 135px;
    object-fit: cover;
    border: 3px solid var(--highlight-yellow);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}

.evaluation-details {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 8px;
}

.evaluation-detail {
    padding: 12px 14px;
    background: var(--card-gradient);
    border-left: 4px solid var(--primary-blue);
    border-radius: var(--radius-md);
    overflow-wrap: anywhere;
}

.evaluation-detail span,
.evaluation-detail strong {
    display: block;
}

.evaluation-detail span {
    color: var(--gray-600);
    font-size: 0.83rem;
}

.evaluation-detail strong {
    color: var(--gray-900);
    margin-top: 3px;
}

.report-section {
    margin-top: 42px;
    page-break-inside: auto;
}

.report-section .section-header {
    margin-bottom: 24px;
    border-bottom-color: var(--primary-blue);
}

.report-section .section-header h2 {
    font-size: clamp(1.45rem, 3vw, 2rem);
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 28px;
}

.summary-card {
    padding: 20px;
    border-radius: var(--radius-lg);
    background: var(--card-gradient);
    border: 1px solid var(--gray-200);
    text-align: center;
}

.summary-label,
.summary-number,
.summary-text {
    display: block;
}

.summary-label {
    color: var(--gray-600);
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.summary-number {
    color: var(--primary-blue-dark);
    font-family: var(--font-primary);
    font-size: 2rem;
}

.summary-text {
    color: var(--accent-green);
    font-size: 1.15rem;
    overflow-wrap: anywhere;
}

.scores-layout {
    display: grid;
    grid-template-columns: 190px minmax(0, 1fr);
    gap: 28px;
    align-items: start;
}

.average-chart-panel,
.skills-panel {
    padding: 20px;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: var(--white);
}

.average-chart-panel {
    border: 2px solid var(--highlight-yellow);
}

.average-chart-panel > h3,
.skills-panel > h3 {
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 20px;
}

.scores-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(115px, 1fr));
    gap: 22px 12px;
}

.score-card {
    text-align: center;
    min-width: 0;
}

.donut-chart {
    --score-angle: 0deg;
    width: 112px;
    height: 112px;
    margin: 0 auto 12px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: conic-gradient(
        var(--accent-green) 0deg var(--score-angle),
        var(--gray-200) var(--score-angle) 360deg
    );
    position: relative;
}

.donut-inner {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    background: var(--white);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1px;
}

.donut-value {
    font-family: var(--font-primary);
    font-weight: 700;
    font-size: 1.35rem;
    color: var(--gray-900);
}

.donut-percent {
    font-size: 0.8rem;
    color: var(--gray-600);
}

.score-card h3 {
    font-family: var(--font-secondary);
    font-size: 0.95rem;
    color: var(--gray-800);
    overflow-wrap: anywhere;
}

.average-card .donut-chart {
    width: 130px;
    height: 130px;
}

.average-card .donut-inner {
    width: 92px;
    height: 92px;
}

.average-card .donut-value {
    font-size: 1.6rem;
}

.scores-table-container {
    margin-top: 26px;
    overflow-x: auto;
}

.scores-table {
    width: 100%;
    border-collapse: collapse;
}

.scores-table th,
.scores-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--gray-200);
    text-align: left;
}

.scores-table th {
    background: var(--primary-blue);
    color: var(--gray-900);
    font-family: var(--font-primary);
}

.scores-table tbody tr:nth-child(even) {
    background: var(--gray-50);
}

/* Capçalera Pass/No pass sense contorn addicional */
.scores-table .pass-status-heading {
    text-align: center !important;
    vertical-align: middle;
}

.score-cell {
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}

.pedagogy-section {
    margin: 28px 0;
}

/* Una sola fila: el nombre de columnes es calcula segons els elements. */
.pedagogy-grid.strengths-grid,
.pedagogy-grid.improvements-grid {
    display: grid;
    gap: 16px;
    align-items: stretch;
    grid-auto-flow: column;
}
.pedagogy-grid.strengths-grid > .strength-card,
.pedagogy-grid.improvements-grid > .improvement-card {
    min-width: 0;
}

.pedagogy-section > h3,
.balance-card > h3 {
    color: var(--accent-green);
    font-size: 1.35rem;
    margin-bottom: 16px;
}

.pedagogy-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.pedagogy-card {
    padding: 20px;
    border-radius: var(--radius-lg);
    background: var(--card-gradient);
    border: 1px solid var(--gray-200);
    border-top: 4px solid var(--primary-blue);
    break-inside: avoid;
}

.strength-card {
    border-top-color: var(--accent-green);
}

.improvement-card {
    border-top-color: var(--secondary-yellow-dark);
}

.pedagogy-card p {
    margin-top: 12px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.pedagogy-score {
    color: var(--gray-800);
    font-family: var(--font-primary);
    font-weight: 700;
    margin-top: 10px;
}

.skill-badge {
    display: inline-block;
    padding: 5px 12px;
    background: var(--primary-blue);
    color: var(--gray-900);
    border-radius: var(--radius-full);
    font-size: 0.82rem;
    font-weight: 700;
}

.improvement-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    flex-wrap: wrap;
}

.improvement-header h3 {
    font-size: 1.15rem;
}

.priority-badge {
    display: inline-block;
    border-radius: var(--radius-full);
    padding: 4px 10px;
    font-size: 0.8rem;
    font-weight: 700;
}

.priority-high {
    background: #fee2e2;
    color: #991b1b;
}

.priority-medium {
    background: #fef3c7;
    color: #92400e;
}

.priority-low {
    background: #dcfce7;
    color: #166534;
}

.balance-card {
    margin: 28px 0;
    padding: 24px;
    background: var(--card-gradient);
    border-left: 5px solid var(--accent-green);
    border-radius: var(--radius-lg);
    break-inside: avoid;
}

.balance-card p {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.activities-list {
    display: grid;
    gap: 18px;
}

.activity-card {
    display: grid;
    grid-template-columns: 44px minmax(0, 1fr);
    gap: 18px;
    padding: 22px;
    border: 1px solid var(--gray-200);
    border-radius: var(--radius-lg);
    background: var(--card-gradient);
    break-inside: avoid;
}

.activity-number {
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: var(--accent-green);
    color: var(--white);
    font-family: var(--font-primary);
    font-size: 1.15rem;
    font-weight: 700;
}

.activity-content > h3 {
    margin: 12px 0 18px;
    font-size: 1.2rem;
    overflow-wrap: anywhere;
}

.activity-field,
.activity-objective {
    margin-top: 14px;
}

.activity-field h4,
.activity-objective h4 {
    color: var(--accent-green);
    font-size: 1rem;
    margin-bottom: 6px;
}

.activity-content p {
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.activity-objective {
    padding: 14px;
    background: rgba(110, 193, 228, 0.14);
    border-radius: var(--radius-md);
}

.teacher-report-section {
    page-break-before: auto;
}

.teacher-comment-card {
    padding: 26px;
    background: var(--gray-50);
    border: 2px solid var(--primary-blue);
    border-left: 6px solid var(--accent-green);
    border-radius: var(--radius-lg);
    break-inside: avoid;
}

.teacher-comment-label {
    display: inline-block;
    background: var(--primary-blue);
    color: var(--gray-900);
    padding: 6px 12px;
    border-radius: var(--radius-full);
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 12px;
}

.teacher-comment-intro {
    color: var(--gray-600);
    font-size: 0.9rem;
    margin-bottom: 16px;
}

.teacher-comment-text {
    color: var(--gray-800);
    font-size: 1.05rem;
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.teacher-signature {
    margin-top: 22px;
    padding-top: 14px;
    border-top: 1px solid var(--gray-300);
    color: var(--gray-600);
}

.empty-message {
    padding: 16px;
    color: var(--gray-600);
    background: var(--gray-50);
    border-radius: var(--radius-md);
}

.report-footer {
    margin-top: 42px;
    padding: 18px 16px;
    border-top: 0;
    background: #fff;
    color: var(--gray-700);
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
    text-align: center;
    font-size: 0.85rem;
}

@media (max-width: 768px) {
    .report-container {
        padding: 20px;
    }

    .header-visual-row {
        grid-template-columns: minmax(100px, 120px) minmax(0, 1fr) 90px;
        gap: 10px;
    }

    .brand-text {
        font-size: .85rem;
    }

    .brand-subtext {
        font-size: .72rem;
    }

    .report-heading {
        text-align: center;
    }

    .header-info-row {
        grid-template-columns: 1fr;
    }

    .contact-footer {
        flex-wrap: wrap;
        justify-content: center;
    }

    .student-photo {
        width: 85px;
        height: 105px;
    }

    .evaluation-details {
        grid-template-columns: 1fr;
    }

    .summary-grid {
        grid-template-columns: 1fr;
    }

    .scores-layout {
        grid-template-columns: 1fr;
    }

    .pedagogy-grid {
        grid-template-columns: 1fr;
    }

    .report-section .section-header h2 {
        font-size: 1.5rem;
    }
}


/* Requisitos de cabecera, barra de superación y contacto */
.header-visual-row {
    display: grid;
    grid-template-columns: minmax(100px, 160px) minmax(0, 1fr) 110px;
    align-items: center;
    gap: 20px;
    width: 100%;
}
.header-info-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-top: 12px;
}
.header-info-item {
    min-width: 0;
    padding: 10px 12px;
    background: var(--gray-50);
    border-radius: var(--radius-md);
    border-left: 3px solid var(--primary-blue);
    overflow-wrap: anywhere;
}
.header-info-item span,
.header-info-item strong {
    display: block;
}
.header-info-item span {
    color: var(--gray-600);
    font-size: .8rem;
    margin-bottom: 3px;
}
.header-info-item strong {
    color: var(--gray-900);
    font-size: .92rem;
}
.report-header {
    display: block;
}
.average-card .donut-chart {
    background: conic-gradient(
        var(--primary-blue) 0deg var(--score-angle),
        var(--gray-200) var(--score-angle) 360deg
    );
}
.average-card .donut-value,
.average-card .donut-percent {
    color: var(--primary-blue-dark);
}
.pass-status-heading {
    text-align: center !important;
    vertical-align: middle;
    white-space: nowrap;
}
.pass-status-cell {
    min-width: 190px;
    vertical-align: middle;
}
.pass-bar-component {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 10px 8px 14px;
    min-width: 210px;
}
.pass-bar-horizontal-wrap {
    width: 100%;
    min-width: 180px;
    padding: 4px 7px 8px;
}
.pass-bar-horizontal {
    width: 100%;
    height: 16px;
    margin-top: 0;
    border-radius: 8px;
    background: linear-gradient(to right, #e53935 0%, #f4d800 50%, #43a047 100%);
}
.pass-bar-scale-labels {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    color: var(--gray-600);
    font-size: .68rem;
}
.pass-bar-horizontal .pass-threshold-marker {
    top: -4px;
    bottom: -4px;
    left: var(--marker-position);
    width: 3px;
    height: auto;
    transform: translateX(-50%);
}
.pass-bar-horizontal .pass-score-marker {
    top: 50%;
    bottom: auto;
    left: var(--marker-position);
    transform: translate(-50%, -50%);
}
.pass-bar-horizontal .pass-score-value {
    top: 13px;
    left: 50%;
    transform: translateX(-50%);
    padding: 1px 3px;
    background: #fff;
    border-radius: 3px;
}
.pass-bar-details {
    min-width: 105px;
    max-width: 145px;
    overflow-wrap: anywhere;
}

.pass-bar {
    position: relative;
    width: 100%;
    height: 16px;
    border-radius: 8px;
    background: linear-gradient(
        to right,
        #e53935 0%,
        #f4d800 50%,
        #43a047 100%
    );
    overflow: visible;
    isolation: isolate;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
}

.pass-threshold-marker {
    position: absolute;
    z-index: 2;
    top: -4px;
    bottom: -4px;
    left: var(--marker-position);
    width: 3px;
    background: #172554;
    border: 1px solid #fff;
    box-shadow: 0 0 0 1px #172554;
    transform: translateX(-50%);
}

.pass-score-marker {
    position: absolute;
    z-index: 3;
    top: 50%;
    left: var(--marker-position);
    width: 12px;
    height: 12px;
    border: 2px solid #fff;
    border-radius: 50%;
    background: #172554;
    box-shadow: 0 0 0 1px #172554;
    transform: translate(-50%, -50%);
}

.pass-score-value {
    position: absolute;
    top: 13px;
    left: 50%;
    color: var(--primary-blue-dark);
    font-size: .72rem;
    font-weight: 800;
    white-space: nowrap;
    transform: translateX(-50%);
}

.pass-bar-scale {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    margin-top: 17px;
    color: var(--gray-600);
    font-size: .68rem;
    line-height: 1.2;
}

.pass-mark-label {
    font-weight: 700;
    text-align: center;
}

.pass-result-label {
    display: block;
    width: 100%;
    box-sizing: border-box;
    min-width: 0;
    margin: 9px 0 0;
    padding: 6px 14px;
    border: 2px solid currentColor;
    border-radius: 999px;
    font-size: 1rem;
    line-height: 1.2;
    font-weight: 900;
    letter-spacing: .02em;
    text-align: center;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0, 0, 0, .12);
}

.pass-result-label.exam-status-pass {
    color: #166534;
    background: #dcfce7;
}
.pass-result-label.exam-status-no-pass {
    color: #991b1b;
    background: #fee2e2;
}
.pass-result-label.exam-status-unavailable {
    color: #374151;
    background: #f3f4f6;
}
.report-footer-caption {
    margin: 0 0 12px;
    padding: 8px 10px;
    background: #fff;
    color: var(--gray-700);
}
.footer-separator {
    margin: 0 7px;
}
.footer-school-name {
    white-space: nowrap;
    font-weight: 700;
}
.contact-footer {
    display: flex;
    padding: 12px 10px;
    border-radius: var(--radius-sm);
    background: var(--highlight-yellow);
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
    align-items: center;
    justify-content: space-between;
    gap: 10px 16px;
    flex-wrap: nowrap;
    font-size: .76rem;
    text-align: left;
}
.contact-footer a {
    color: var(--gray-700);
    text-decoration: none;
    white-space: nowrap;
}
.contact-footer a:hover {
    color: var(--primary-blue-dark);
    text-decoration: underline;
}

@media print {
    @page {
        size: A4 landscape;
        margin: 10mm;
    }

    body.student-report {
        padding: 0;
        background: white;
        font-size: 10pt;
        color: #222;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    .report-container {
        max-width: none;
        padding: 0;
        border-radius: 0;
        box-shadow: none;
    }

    .no-print {
        display: none !important;
    }

    .report-section {
        margin-top: 24px;
    }

    .section-header {
        margin-bottom: 14px !important;
    }

    .report-header,
    .summary-card,
    .pedagogy-card,
    .balance-card,
    .activity-card,
    .teacher-comment-card {
        break-inside: avoid;
    }

    .activity-card,
    .pedagogy-card,
    .teacher-comment-card,
    .balance-card {
        box-shadow: none;
    }

    .report-heading h1 {
        font-size: 21pt;
    }

    .report-section .section-header h2 {
        font-size: 16pt;
    }

    .donut-chart,
    .pass-bar,
    .contact-footer,
    .student-photo {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
    }

    .scores-layout,
    .average-chart-panel,
    .skills-panel,
    .scores-table tr,
    .pass-status-cell {
        break-inside: avoid;
        page-break-inside: avoid;
    }

    .report-footer {
        margin-top: 24px;
    }

    .header-info-row {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .contact-footer {
        flex-wrap: nowrap;
        gap: 8px;
        font-size: 7.5pt;
    }

    .contact-footer a {
        white-space: nowrap;
    }
}
"""

    # Escrivimos la hoja de estilos combinada dentro de reports.
    # Así, el HTML es portable junto con informe.css.
    ruta_css_final = carpeta / "informe.css"

    ruta_css_final.write_text(
        css_original + "\n\n" + css_informe,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # 12. GUARDAR EL HTML CON EL IDIOMA EN EL NOMBRE DEL ARCHIVO
    # --------------------------------------------------------

    nom_fitxer = (
        f"informe_{student_id}_{evaluation_date}_{language}.html"
    )

    ruta_html = carpeta / nom_fitxer

    ruta_html.write_text(
        document_html,
        encoding="utf-8"
    )

    return ruta_html




# ============================================================
# 23. RECUPERAR DATOS COMPLEMENTARIOS PER A L'INFORME
# ============================================================

ruta_info_extra = BASE_DIR / "data" / "INF_COMENTARIS_ALUMNES_EJERCICO_TIPUS_CURS.csv"

# Comprobar que el archivo existe
if not Path(ruta_info_extra).is_file():
    raise FileNotFoundError(
        f"No se ha encontrado el archivo complementario: {ruta_info_extra}"
    )

# Leer el archivo complementario
df_info_extra = pd.read_csv(
    ruta_info_extra,
    sep=";",
    encoding="utf-8-sig",
    decimal=",",
)

# Campos necesarios para construir el informe
columnes_extra = [
    "IDALUMNE",
    "IDEVALUACIO",
    "IDCURS",
    "COMENTARI",
    "PROFE",
    "NOMCURS",
    "NOM_ALUMNE",
    "DESCRIPCIO",
    "EJERCICIO_ESCOLAR"
]

# Comprobar que existen todas las columnes necesarias
columnes_faltants = [
    columna for columna in columnes_extra
    if columna not in df_info_extra.columns
]

if columnes_faltants:
    raise ValueError(
        f"Faltan columnas en el archivo complementario: {columnes_faltants}"
    )

# Seleccionar només las columnas necesarias
df_info_extra = df_info_extra[columnes_extra].copy()

# Crear una còpia de df_analisis per no modificar-lo
df_analisis_merge = df_analisis.copy()

# Normalitzar els identificadors
def normalitzar_id(serie):
    return (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )


# Normalitzar les tres llaves en los dos dataframes
for dataframe in [df_analisis_merge, df_info_extra]:
    dataframe["_IDALUMNE_CLAU"] = normalitzar_id(
        dataframe["IDALUMNE"]
    )
    dataframe["_IDEVALUACIO_CLAU"] = normalitzar_id(
        dataframe["IDEVALUACIO"]
    )
    dataframe["_IDCURS_CLAU"] = normalitzar_id(
        dataframe["IDCURS"]
    )

# Claves que utilitzaremos para a la unión
claus = [
    "_IDALUMNE_CLAU",
    "_IDEVALUACIO_CLAU",
    "_IDCURS_CLAU"
]

# Comprobar las claves del archivo complementario
# no esten vacias
if df_info_extra[claus].isna().any().any():
    raise ValueError(
        "Hi ha identificadors buits al fitxer complementari."
    )

if df_info_extra[claus].eq("").any().any():
    raise ValueError(
        "Hi ha identificadors buits al fitxer complementari."
    )

# Comprobar que cada combinación de alumno y evaluación
# y curso aparezcan una sola vez en el archivo complementario
if df_info_extra.duplicated(claus).any():
    raise ValueError(
        "Hi ha combinacions duplicades d'IDALUMNE, "
        "IDEVALUACIO i IDCURS al fitxer complementari."
    )

# Eliminar las columnas identificadoras originales
# del dataframe complementario antes de hacer la unión
df_info_extra_merge = df_info_extra.drop(
    columns=["IDALUMNE", "IDEVALUACIO", "IDCURS"]
)

# Unir los datos manteniendo todas las filas de df_analisis
df_informe_final = df_analisis_merge.merge(
    df_info_extra_merge,
    on=claus,
    how="left",
    validate="many_to_one",
    indicator=True
)

# Avisar si no se ha encontrado la información complementaria
registres_sense_info = df_informe_final[
    df_informe_final["_merge"] == "left_only"
]

if not registres_sense_info.empty:
    print(
        "Avíso: no se ha encontrado información complementaria "
        f"per a {len(registres_sense_info)} registre(s)."
    )

# Eliminar las columnas auxiliares
df_informe_final.drop(
    columns=claus + ["_merge"],
    inplace=True
)

print("Datos complementarios preparados.")
print(f"Registros para el informe: {len(df_informe_final)}")




# ============================================================
# 24. GENERAR EL INFORME HTML
# ============================================================

# Buscar la fila correspondiente al alumno y a la evaluación actuales
fila_informe = df_informe_final[
    (
        normalitzar_id(df_informe_final["IDALUMNE"])
        == normalitzar_id(pd.Series([id_alumne_str])).iloc[0]
    )
    &
    (
        normalitzar_id(df_informe_final["IDEVALUACIO"])
        == normalitzar_id(pd.Series([id_avaluacio])).iloc[0]
    )

    &
    (
        normalitzar_id(df_informe_final["IDCURS"])
        == normalitzar_id(pd.Series([id_curs])).iloc[0]
    )
]

if fila_informe.empty:
    raise ValueError(
        "No se han encontrado los datos del alumno y la evaluación "
        "en df_informe_final."
    )

fila_informe = fila_informe.iloc[0]

# Preparar los datos complementarios para el HTML
info_extra = {
    "student_name": fila_informe["NOM_ALUMNE"],
    "teacher": fila_informe["PROFE"],
    "course": fila_informe["NOMCURS"],
    "evaluation_description": fila_informe["DESCRIPCIO"],
    "school_year": fila_informe["EJERCICIO_ESCOLAR"],
    "teacher_comment": fila_informe["COMENTARI"]
}

# Generar el informe HTML
informe_html = informe if informe is not None else {
    "student_data": student_profile
}

ruta_html = generar_informe_html(
    informe=informe_html,
    language=language,
    info_extra=info_extra,
    carpeta_sortida=BASE_DIR / "reports",
    ruta_css=BASE_DIR / "style.css",
    include_ai_analysis=analisis_ia_activada
)

print(f"Informe HTML generado: {ruta_html}")


from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import uuid
import os
import subprocess
import sys
import threading

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for API
class TaskSchema(BaseModel):
    id: int
    task_number: int
    level: int
    prompt: str
    default_code: str

    class Config:
        from_attributes = True

class LessonSchema(BaseModel):
    id: int
    lesson_number: int
    title: str
    theory_content: str
    tasks: List[TaskSchema] = []

    class Config:
        from_attributes = True

class SaveCodeRequest(BaseModel):
    user_id: str
    task_id: int
    code: str

class ActivityQuestionSchema(BaseModel):
    id: int
    prompt: str
    correct_answer: str
    class Config:
        from_attributes = True

class ActivitySchema(BaseModel):
    id: int
    title: str
    description: str
    default_code: str
    questions: List[ActivityQuestionSchema] = []
    class Config:
        from_attributes = True

class SaveActivityAnswerRequest(BaseModel):
    user_id: str
    activity_id: int
    answers: dict  # e.g., {"1": "0.94"}
    code: str

@app.on_event("startup")
def on_startup():
    database.init_db()
    db = database.SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()


def get_or_create_lesson(db: Session, lesson_number: int, title: str, markdown_file: str = ""):
    theory_content = ""
    if markdown_file and os.path.exists(markdown_file):
        with open(markdown_file, "r", encoding="utf-8") as f:
            md_text = f.read()
        import markdown
        theory_content = markdown.markdown(
            md_text,
            extensions=['tables', 'fenced_code']
        )

    lesson = db.query(database.Lesson).filter(database.Lesson.lesson_number == lesson_number).first()
    if lesson is None:
        lesson = database.Lesson(
            lesson_number=lesson_number,
            title=title,
            theory_content=theory_content,
        )
        db.add(lesson)
    else:
        lesson.lesson_number = lesson_number
        lesson.title = title
        lesson.theory_content = theory_content

    db.commit()
    db.refresh(lesson)
    return lesson


def upsert_task(db: Session, lesson_id: int, task_number: int, level: int, prompt: str, default_code: str = ""):
    existing = db.query(database.Task).filter(
        database.Task.lesson_id == lesson_id,
        database.Task.task_number == task_number,
        database.Task.level == level,
    ).first()

    if existing is None:
        existing = database.Task(
            lesson_id=lesson_id,
            task_number=task_number,
            level=level,
            prompt=prompt,
            default_code=default_code,
        )
        db.add(existing)
        return

    existing.prompt = prompt
    existing.default_code = default_code


def delete_legacy_tasks(db: Session):
    db.query(database.Task).filter(database.Task.prompt.like("%Uppgift%")).delete(synchronize_session=False)


def delete_lesson_by_title(db: Session, title: str):
    lessons = db.query(database.Lesson).filter(database.Lesson.title == title).all()
    if lessons:
        lesson_ids = [lesson.id for lesson in lessons]
        db.query(database.Task).filter(database.Task.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        for lesson in lessons:
            db.delete(lesson)
        db.commit()


def upsert_activity(db: Session, title: str, description: str, default_code: str, questions: list):
    act = db.query(database.Activity).filter(database.Activity.title == title).first()
    if not act:
        act = database.Activity(title=title, description=description, default_code=default_code)
        db.add(act)
        db.commit()
        db.refresh(act)
    else:
        act.description = description
        act.default_code = default_code
        db.commit()

    existing_qs = db.query(database.ActivityQuestion).filter(database.ActivityQuestion.activity_id == act.id).order_by(database.ActivityQuestion.id).all()
    
    for i, q_data in enumerate(questions):
        if i < len(existing_qs):
            existing_qs[i].prompt = q_data["prompt"]
            existing_qs[i].correct_answer = q_data["correct_answer"]
        else:
            new_q = database.ActivityQuestion(activity_id=act.id, prompt=q_data["prompt"], correct_answer=q_data["correct_answer"])
            db.add(new_q)
            
    for i in range(len(questions), len(existing_qs)):
        db.query(database.ActivityAnswer).filter(database.ActivityAnswer.question_id == existing_qs[i].id).delete(synchronize_session=False)
        db.delete(existing_qs[i])
        
    db.commit()
    return act

def seed_activities(db: Session):
    import markdown
    md_file = os.path.join(BASE_DIR, 'content', 'activities', 'bransle.md')
    desc = ""
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
             desc = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])
    
    upsert_activity(
        db,
        title="Bränsleförbrukning",
        description=desc,
        default_code="# --- Fasta omvandlingsfaktorer ---\nLITER_PER_GALLON = 3.785\nKM_PER_MILE = 1.609\nKM_PER_MIL = 10.0\n\n# =====================================================================\n# DEL 1: Från l/mil till MPG\n# =====================================================================\nliter_per_mil_input =    # <-- FYLL I DETTA VÄRDE FÖR ATT LÖSA FRÅGORNA\n\n# 1. Beräkna hur många gallons per svensk mil\ngallon_per_mil = \n\n# 2. Beräkna hur många gallons per mile\ngallon_per_mile = \n\n# 3. Beräkna hur många mile per gallon\nmpg_output = \n\nprint('DEL 1:', liter_per_mil_input, 'l/mil motsvarar', round(mpg_output, 2), 'MPG')\n\n\n# =====================================================================\n# DEL 2: Från MPG till l/mil\n# =====================================================================\nmpg_input =    # <-- FYLL I DETTA VÄRDE FÖR ATT LÖSA FRÅGORNA\n\n# 1. Beräkna hur många gallons per mile\ngallon_per_mile = \n\n# 2. Beräkna hur många gallons per mil\ngallon_per_mil = \n\n# 3. Beräkna hur många liter per mil\nliter_per_mil_output = \n\nprint('DEL 2:', mpg_input, 'MPG motsvarar', round(liter_per_mil_output, 2), 'l/mil')",
        questions=[
            {"prompt": "En modern svensk hybridbil är mycket bränslesnål och drar endast 0,45 l/mil. Vad motsvarar detta i amerikanska Miles per Gallon (MPG)?<br><br>(Ändra värdet i DEL 1, kör koden och svara med närmaste heltal)", "correct_answer": "52"},
            {"prompt": "Du funderar på att importera en äldre amerikansk SUV med en stor V8-motor. Enligt specifikationen har bilen en bränsleekonomi på 14 MPG. Hur många liter bensin drar den per svensk mil (l/mil)?<br><br>(Ändra värdet i DEL 2, kör koden och svara med två decimaler)", "correct_answer": "1.68"},
            {"prompt": "Du är på semester i USA och ska köra en roadtrip med en hyrbil. Sträckan du ska köra motsvarar exakt 45 svenska mil. På bilens instrumentpanel står det att den har en snittförbrukning på 32 MPG.<br><br>Använd ditt program för att först ta reda på bilens förbrukning i l/mil, och räkna sedan ut hur många liter bensin som kommer att gå åt under hela resan.<br><br>(Svara i hela liter, avrunda till närmaste heltal)", "correct_answer": "33"}
        ]
    )

    md_file = os.path.join(BASE_DIR, 'content', 'activities', 'kastparabel.md')
    desc = ""
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
             desc = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])
    
    upsert_activity(
        db,
        title="Kastparabeln",
        description=desc,
        default_code="import numpy as np\nimport matplotlib.pyplot as plt\n\n# =====================================================================\n# INPUTVÄRDEN (Ändra dessa för att lösa uppgifterna)\n# =====================================================================\nv0 =          # Utgångshastighet i m/s\ng =           # Tyngdacceleration (Jorden = 9.8)\nt_slut =      # Hur lång tidsperiod vi vill analysera (i sekunder)\n\n# --- Beräkning med NumPy ---\n# Skapar 1001 jämnt fördelade tidssteg från 0 till t_slut\nt = np.linspace(0, t_slut, 1001)\n\n# Formeln beräknas för ALLA 1001 tidspunkter samtidigt!\nh = v0 * t - g * t**2 / 2\n\n# Kod för att hitta högsta höjd\nmax_hojd = np.max(h)\n\n# Kod för att hitta landningstiden:\n# Vi letar efter första indexet där t > 0.1 (efter start) OCH höjden h <= 0\nlandat_indices = np.where((t > 0.1) & (h <= 0))[0]\n\nif len(landat_indices) > 0:\n    landnings_tid = t[landat_indices[0]]\nelse:\n    landnings_tid = None  # Bollen har inte hunnit landa innan t_slut\n\n# --- Skriv ut det numeriska resultatet i terminalen ---\nprint('--- ANALYS AV KASTET (0 till {t_slut} sekunder) ---')\nprint('Högsta höjd som bollen når:', round(max_hojd, 1), 'meter')\n\nif landnings_tid is not None:\n    print('Bollen landar på marken efter:', round(landnings_tid, 2), 'sekunder')\nelse:\n    print('Bollen har inte landat än! Höj t_slut för att se landningen.')\n\n# --- Visualisering med PyPlot ---\nplt.figure(figsize=(8, 5))\nplt.plot()  # Plotta t och h med någon färg och linjebredd\n\n# Designa grafen\nplt.title('Kastparabel', fontsize=14)\nplt.xlabel(   )  # Sätt en label för x-axeln\nplt.ylabel(   )  # Sätt en label för y-axeln\nplt.grid(True, linestyle='--', alpha=0.6)  # Lägger till ett rutnät\nplt.axhline(0, color='black', linewidth=1.5)  # Markera marknivån (0 meter)\n\n# Visa fönstret med grafen\nplt.show()",
        questions=[
            {"prompt": "En fotboll sparkas rakt upp i luften på jorden (där <math><mi>g</mi><mo>=</mo><mn>9,8</mn></math> m/s²) med en hög utgångshastighet på <math><msub><mi>v</mi><mn>0</mn></msub><mo>=</mo><mn>32</mn></math> m/s. Vi vill analysera bollen fram tills den landar, vilket tar ungefär 6,5 sekunder. <br><br>Vilken är den absolut högsta höjden (i meter) som bollen når innan den vänder nedåt? (Svara med en decimal)", "correct_answer": "52,2"},
            {"prompt": "Vi behåller samma spark på jorden (<math><msub><mi>v</mi><mn>0</mn></msub><mo>=</mo><mn>32</mn></math> m/s och <math><mi>g</mi><mo>=</mo><mn>9,8</mn></math> m/s²). Om du kollar på grafen från förra uppgiften ser du att den klipper av precis innan bollen slår i marken. Öka <code>t_slut</code> så att du ser landningen.<br><br>Efter hur många sekunder landar bollen på marken igen? (Svara med två decimaler)", "correct_answer": "6.53"},
            {"prompt": "Tänk dig nu att vi flyttar samma experiment till månen. Där är gravitationen mycket svagare, så tyngdaccelerationen är bara <math><mi>g</mi><mo>=</mo><mn>1,6</mn></math> m/s². Vi skjuter upp bollen med samma utgångshastighet (<math><msub><mi>v</mi><mn>0</mn></msub><mo>=</mo><mn>32</mn></math> m/s). Eftersom månen har så svag gravitation kommer bollen att flyga extremt högt och vara i luften under en mycket längre tid.<br><br>Ändra värdet för <math><mi>g</mi></math> och testa dig fram genom att höja <code>t_slut</code> tills du ser bollen landa i grafen. <br><br>Vilken blir bollens högsta höjd (i meter) på månen innan den vänder nedåt? (Svara i hela meter)", "correct_answer": "320"}
        ]
    )

    md_file = os.path.join(BASE_DIR, 'content', 'activities', 'bageri.md')
    desc = ""
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
             desc = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])
    
    upsert_activity(
        db,
        title="Bageriet",
        description=desc,
        default_code="# --- Målvärden för resurser (fyll i dessa för att lösa uppgifterna) ---\nMAL_MJOL = \nMAL_TID = \n\n# Variabler för att hålla reda på den bästa optimeringen\nmax_vinst = 0\nbasta_x = 0\nbasta_y = 0\n\n# Vi testar alla kombinationer av x och y mellan 0 och 100\nfor x in range(   ):      # x = Antal surdegsbröd\n    for y in range(   ):  # y = Antal lyxbullar\n        # Räkna ut hur mycket resurser just denna kombination kräver\n        mjol_som_kravs = \n        tid_som_kravs = \n\n        # Räkna ut vilken vinst just denna kombination ger\n        vinst = \n\n        # ===================================================================\n        # DEL A: Ekvationssystem (exakt matchning)\n        # ===================================================================\n        # Lägg in en if-sats för målvärdena\n            # Utskrift för hittad lösning\n            print('Hittade en exakt lösning -> Bröd (x):', x, 'st, Bullar (y):', y, 'st')\n\n\n        # ===================================================================\n        # DEL B: Linjär optimering (maximal vinst inom begränsningar)\n        # ===================================================================\n        # Lägg in en if-sats för målvärde och villkor\n            # Kontrollera om vinst är bättre än den bästa hittills\n                # Spara i sådana fall den nya bästa vinsten och vilka x och y som gav den\n\n\n# Print-funktionen för Del B (avaktiverad från början)\n# print('Maximal vinst blir:', max_vinst, 'kr (Bröd:', basta_x, 'st, Bullar:', basta_y, 'st)')",
        questions=[
            {"prompt": "Efter en intensiv arbetsdag märker bagarna att de har använt exakt 9 000 g mjöl och att det har tagit exakt 270 minuter totalt.<br><br>Hur många lyxbullar <math><mi>y</mi></math> bakades under dagen?", "correct_answer": "30"},
            {"prompt": "En annan dag har tidtagaruret gått sönder, så vi vet inte hur många minuter det tog. Vi vet däremot att de använde exakt 7 000 g mjöl. Det finns flera olika heltalskombinationer som uppfyller detta. Men vi har en extra ledtråd: bageriet råkade baka exakt dubbelt så många bullar som bröd <math><mi>y</mi><mo>=</mo><mn>2</mn><mi>x</mi></math>.<br><br>Hur många surdegsbröd <math><mi>x</mi></math> bakade de den dagen?", "correct_answer": "10"},
            {"prompt": "Nu ska vi optimera! Inför helgen har bageriet fått en fast mängd råvaror och tid. De har maximalt 10 000 g mjöl tillgodo, och bagarna kan arbeta i maximalt 300 minuter. Det behöver inte gå jämnt ut, men de vill tjäna så mycket pengar som möjligt.<br><br>Vilken är den absolut maximala vinsten bageriet kan göra under dessa begränsningar?", "correct_answer": "1030"}
        ]
    )

    md_file = os.path.join(BASE_DIR, 'content', 'activities', 'turtle.md')
    desc = ""
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
             desc = markdown.markdown(f.read(), extensions=['tables', 'fenced_code'])
    
    upsert_activity(
        db,
        title="Turtlekonst",
        description=desc,
        default_code="import turtle\n\n# =====================================================================\n# STARTVÄRDEN (Ändra dessa värden för att lösa uppgifterna)\n# =====================================================================\nantal_linjer = \nvinkel = \nstart_langd = \nlangd_okning = \n\n# --- Mätvariabler (Rör ej dessa) ---\ntotal_stracka = 0\ntotal_rotation = 0\n\n# --- Setup för sköldpaddan ---\nt = turtle.Turtle()\nt.speed(0)  # Maxhastighet\n\nlangd = start_langd\n\n# --- Loopen som skapar konsten och mäter matematiken ---\nfor i in range(antal_linjer):\n    t.forward(langd)\n    t.left(vinkel)\n\n    # Datorn mäter vad den precis gjorde\n    total_stracka = \n    total_rotation = \n\n    # Linjen blir längre till nästa varv (Aritmetisk ökning)\n    langd = \n\n# --- Skriv ut den numeriska mätdatan ---\nprint('--- GEOMETRISK MÄTDATA ---')\nprint('Antal ritade linjer:', antal_linjer, 'st')\nprint('Total sträcka:', total_stracka, 'pixlar')\nprint('Total rotation:', total_rotation, 'grader')\n\n# Håller fönstret öppet\nturtle.done()",
        questions=[
            {"prompt": "En designer vill använda en fyrkantsspiral som bas för en logotyp. Mönstret ska bestå av exakt <strong>80 linjer</strong>, startlängden ska vara <strong>10 pixlar</strong>, längdökningen ska vara <strong>3</strong> och vinkeln ska vara exakt <strong>90 grader</strong>.<br><br>Ställ in dessa värden överst i koden, gör färdigt programmet och kör det. <br><br>Vilken total sträcka (i pixlar) har sköldpaddan vandrat när logotypen är klar?", "correct_answer": "10280"},
            {"prompt": "Du ändrar mönstret till en stjärnspiral genom att sätta vinkeln till <strong>144 grader</strong>. Du låter programmet rita <strong>35 linjer</strong>. När programmet har kört klart har sköldpaddan snurrat ett stort antal grader totalt.<br><br>Hur många hela varv (ett varv = 360°) har sköldpaddan snurrat runt sin egen axel totalt?", "correct_answer": "14"},
            {"prompt": "Du vill rita en mjuk, rund spiral (en så kallad arkimedisk spiral). För att göra den rund måste vinkeln vara väldigt liten, så du sätter vinkeln till 10 grader. Startlängden ska vara 1. Dessutom vill du att spiralen ska växa mycket långsammare, så du ändrar variabeln <code>langd_okning</code> till 0,2.<br><br>Du vill att sköldpaddan ska snurra exakt <strong>5 hela varv</strong> (<math><mn>5</mn><mo>&sdot;</mo><mn>360</mn><mo>&deg;</mo><mo>=</mo><mn>1800</mn><mo>&deg;</mo></math>). Räkna ut hur många linjer som krävs för att sköldpaddan ska hinna snurra totalt 1800 grader om den svänger 10 grader per linje. Ändra koden och kör programmet. <br><br>Vad blir den totala sträckan för denna runda spiral? (Svara med närmaste heltal)", "correct_answer": "3402"}
        ]
    )

def seed_db(db: Session):
    seed_activities(db)
    delete_legacy_tasks(db)
    lesson1 = get_or_create_lesson(
        db,
        1,
        "Utskrifter och beräkningar",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson1.md')
    )
    upsert_task(db, lesson1.id, 1, 1, "Skriv ut texten 'Hej mattegeni!'.", "print()")
    upsert_task(db, lesson1.id, 2, 1, "Skriv ut talet 42.", "")
    upsert_task(db, lesson1.id, 3, 1, "Skriv ut texten 'Svaret är' följt av talet 42 på samma rad.", "print('Svaret är', )")
    upsert_task(db, lesson1.id, 4, 1, "Låt programmet beräkna 15 + 23 och skriv ut resultatet.", "")
    upsert_task(db, lesson1.id, 5, 1, "Låt programmet beräkna 100 - 34 / 2 och skriv ut resultatet.", "")
    upsert_task(db, lesson1.id, 1, 2, "Skriv ut kostnaden för två tröjor och ett par jeans. Du vet att en tröja kostar 199 kr och ett par jeans kostar 799 kr.<br><i>Tänk på att det är programmet som ska göra beräkningen.</i>", "print('Det kommer att kosta', , 'kr.')")
    upsert_task(db, lesson1.id, 2, 2, "Gör en tydlig utskrift av hur långt man kommer på 2,5 timmar om man kör med hastigheten 60 km/h.<br><i>Tänk på att det är programmet som ska göra beräkningen.</i>", "print('Om du kör...', )")
    upsert_task(db, lesson1.id, 3, 2, "Beräkna <math><mfrac><mi>9</mi> <mi>3</mi></mfrac></math> och <math><mfrac><mi>10</mi> <mi>3</mi></mfrac></math> med både <code>/</code> och <code>//</code> och skriv ut resultatet. Jämför resultaten.", "")
    upsert_task(db, lesson1.id, 4, 2, "Det finns ett räknesätt som man i Python skriver <code>**</code> för att få. Beräkna <code>2**2</code>, <code>2**3</code> och <code>3**2</code> och skriv ut resultaten. Vad är det för räknesätt?", "print('2**2 =', 2**2)\nprint('2**3 =', )")
    upsert_task(db, lesson1.id, 5, 2, "Du har 500 kr. Du köper 4 glassar: 2 strutar för 29,30 kr/st och 2 pinnglassar för 18,90 kr/st. Skriv ett program som beräknar och skriver ut hur mycket pengar du har kvar.", "")

    lesson2 = get_or_create_lesson(
        db,
        2,
        "Variabler",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson2.md')
    )
    upsert_task(db, lesson2.id, 1, 1, "Skapa en variabel <code>x</code> och ge den värdet 10. Skapa en variabel <code>y</code> och ge den värdet 4. Skriv sedan ut <code>x+y</code> och <code>x*y</code>.", "")
    upsert_task(db, lesson2.id, 2, 1, "Skapa en variabel <code>namn</code> och ge den ditt eget namn som värde. Skriv ut 'Hej' följt av <code>namn</code> och ett utropstecken.", "")
    upsert_task(db, lesson2.id, 3, 1, "Skapa en variabel <code>troj_pris</code> och lagra talet 199 i den. Skapa en variabel <code>jeans_pris</code> och lagra talet 799 i den. Beräkna med hjälp av variablerna kostnaden för två tröjor och ett par jeans och skriv ut det.", "")
    upsert_task(db, lesson2.id, 4, 1, "Skriv ett program som beräknar arean av en triangel med hjälp av variablerna <code>bas</code> och <code>hojd</code>. Arean ska sparas i varibeln <code>area</code>. Gör en tydlig utskrift av arean. <br>Provkör programmet med några olika värden på <code>bas</code> och <code>hojd</code>.", "print('En triangel med basen', )")
    upsert_task(db, lesson2.id, 5, 1, "Vilka av dessa variabelnamn är ogiltiga i Python? Avkommentera en i taget och testa för att se vilka som ger ett felmeddelande.", "# 1_plats = 'kalle'\n# min_alder = 16\n# for-namn = 'Lisa'")
    upsert_task(db, lesson2.id, 1, 2, "Max har skrivit ett program som beräknar arean av en triangel. Tyvärr blir det ett felmeddelande (<code>NameError: name 'Bas' is not defined</code>) när han ska köra programmet. Rätta felen så att programmet fungerar som det ska. ", "bas = 5\nhojd = 3\nprint('Arean är', Bas * Höjd / 2, 'cm².')")
    upsert_task(db, lesson2.id, 2, 2, "Skriv ett program som lagrar din längd i cm en variabel. Skriv sedan ut din längd i meter med hjälp av variabeln.", "")
    upsert_task(db, lesson2.id, 3, 2, "Med formeln <math><mi>F</mi><mo>=</mo><mi>1,8</mi><mi>C</mi><mo>+</mo><mi>32</mi></math> kan man omvandla från en temperatur i grader Celsius till grader Fahrenheit. Använd tre variabler för tre olika temperaturer i Celsius och skriv ut motsvarande temperaturer i grader Fahrenheit.", "print('0 &#8451; är', , '&#8457;')\nprint('37 &#8451; är', , '&#8457;')\nprint('100 &#8451; är', , '&#8457;')")
    upsert_task(db, lesson2.id, 4, 2, "<ol><li>Skapa en variabel <code>antal_katter</code> och sätt den till 3.</li><li>Skapa en variabel <code>antal_hundar</code> och sätt den till <code>antal_katter</code>.</li><li>Öka värdet på <code>antal_katter</code> med 2.</li><li>Skriv ut både <code>antal_hundar</code> och <code>antal_katter</code>.</li></ol>Fungerar det som du trodde?", "")
    upsert_task(db, lesson2.id, 5, 2, "Talet &pi; finns i något som heter <code>math</code> och som vi kan importera. Lagra radien 5 i en variabel <code>radie</code>. Beräkna och skriv ut cirkelns omkrets och area med hjälp av <code>math.pi</code> och variabeln.", "import math\nprint(math.pi)\nprint('Omkretsen är', )\nprint('Arean är', )")

    lesson3 = get_or_create_lesson(
        db,
        3,
        "Inmatningar",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson3.md')
    )
    upsert_task(db, lesson3.id, 1, 1, "Använd <code>input()</code> för att fråga användaren 'Vad är din favoritfärg? ' och spara svaret i en variabel. Skriv sedan ut variabeln.", "favoritfarg = ")
    upsert_task(db, lesson3.id, 2, 1, "Använd <code>input()</code> för att fråga efter användarens namn, och skriv sedan ut 'Hej ' följt av namnet och ett utropstecken.", "")
    upsert_task(db, lesson3.id, 3, 1, "Be användaren mata in sin ålder (som ett heltal) och spara den i en variabel. Skriv sedan ut åldern med en lämplig text.", "")
    upsert_task(db, lesson3.id, 4, 1, "Fråga användaren hur långa de är i meter. Skriv ut längden i cm med en lämplig text. Längden i cm ska vara ett heltal.", "")
    upsert_task(db, lesson3.id, 5, 1, "Fråga användaren efter basen och höjden på en triangel. Beräkna arean och skriv ut den.", "")
    upsert_task(db, lesson3.id, 1, 2, "Det är 20% rabatt i en butik. Skriv ett program som frågar efter varans ursprungliga pris och skriver ut priset med rabatt. Avrunda priset till 2 decimaler med hjälp av <code>round()</code>.", "")
    upsert_task(db, lesson3.id, 2, 2, "Moms på kläder är 25%. Fråga efter ett pris exklusive moms och skriv ut priset inklusive moms avrundat till 2 decimaler.", "")
    upsert_task(db, lesson3.id, 3, 2, "Skapa ett litet miniräknarprogram som frågar efter två tal och skriver ut summan, differensen och produkten.", "")
    upsert_task(db, lesson3.id, 4, 2, "Den som reser till sin arbetsplats kan ha rätt att göra avdrag för resor. För bil är det 25 kr/mil. Skriv ett program som frågar efter avståndet till arbetsplatsen och antalet arbetsdagar och räknar ut avdraget. Presentera svaret i en lämplig utskrift och avrunda till 0 decimaler.", "")
    upsert_task(db, lesson3.id, 5, 2, "Elena ska ha inflyttningsfest. Hon vill köpa pizza och läsk till alla gäster. <ul><li>Hon ska köpa läsk i 1,5-liters flaskor. Hon räknar med att varje person ska få 0,5 liter läsk.</li><li>Hon räknar med att dela varje pizza i åtta delar och att alla äter tre bitar var.</li></ul>Skriv ett program som frågar efter hur många gäster det blir och beräknar antalet flaskor och pizzor hon måste hon köpa. <br><br>Eftersom hon bara kan köpa <strong>hela</strong> flaskor och pizzor och hon vill att alla ska få tillräckligt med mat och dryck behöver vi avrunda uppåt. Det finns en funktion i <code>math</code> som heter <code>math.ceil()</code> som gör just det.", "import math\nresultat = math.ceil(4.2)\nprint(resultat)\n")

    lesson4 = get_or_create_lesson(
        db,
        4,
        "For-satsen och range",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson4.md')
    )
    upsert_task(db, lesson4.id, 1, 1, "Skriv ut talen 0 till 4 med en for-loop och range.", "")
    upsert_task(db, lesson4.id, 2, 1, "Skriv ut talen 1 till 10 med en for-loop och range.", "")
    upsert_task(db, lesson4.id, 3, 1, "Skriv ut de jämna talen 2, 4, 6, 8 och 10 med en for-loop och range.", "")
    upsert_task(db, lesson4.id, 4, 1, "Använd en loop för att beräkna summan av 1 + 2 + 3 + 4 + 5 och skriv ut resultatet.", "summa = 0\n")
    upsert_task(db, lesson4.id, 5, 1, "Skriv ut texten 'Matte! ' fem gånger på två olika sätt:<ul><li>med hjälp av en for-loop och range</li><li>med hjälp av text-multiplikation (se <q>Inmatningar</q>).</li></ul>", "")
    upsert_task(db, lesson4.id, 1, 2, "Skriv ut treans multiplikationstabell med hjälp av en loop. Exempel på utskrift:<br><code>3 * 1 = 3<br>3 * 2 = 6<br>...<br>3 * 10 = 30</code>", "")
    upsert_task(db, lesson4.id, 2, 2, "Skriv ett program som räknar ut arean för rektanglar med ena sidan 4 och den andra sidan 2, 3, 4, 5 och 6. Skriv ut varje area med en loop. Exempel på utskrift:<br><code>Arean för rektangel 4 * 2 = 8<br>Arean för ...</code>", "")
    upsert_task(db, lesson4.id, 3, 2, "Fakultet är en funktion inom matematiken. För ett heltal större än noll är fakulteten lika med produkten av alla heltal från 1 upp till och med talet självt. Fakultet skrivs med <math>!</math>. Till exempel är <math>3! = 1 &sdot; 2 &sdot; 3 = 6</math>.<br><br>Skriv ett program som beräknar 5! med en loop och skriver ut resultatet.", "produkt = 1\n")
    upsert_task(db, lesson4.id, 4, 2, "Beräkna summan av alla tal från 1 till 99 med en loop och skriv ut resultatet.<br><br>Det finns en formel för denna summa: <math><msub><mi>S</mi><mn>n</mn></msub><mo>=</mo><mi>n</mi><mfrac><mrow><msub><mi>a</mi><mn>1</mn></msub><mo>+</mo><msub><mi>a</mi><mn>n</mn></msub></mrow><mi>2</mi></mfrac></math> där <math><mi>n</mi></math> = antalet termer, <math><msub><mi>a</mi><mn>1</mn></msub></math> = det första talet i talföljden <math><msub><mi>a</mi><mn>n</mn></msub></math> = det sista talet i talföljden. Kontrollräkna programmets svar med hjälp av formeln.", "summa = 0\n")
    upsert_task(db, lesson4.id, 5, 2, "Beräkna summan av alla jämna tal från 2 till 200 med en loop och skriv ut resultatet.<br><br>Det finns en formel för denna summa: <math><msub><mi>S</mi><mn>n</mn></msub><mo>=</mo><mi>n</mi><mfrac><mrow><msub><mi>a</mi><mn>1</mn></msub><mo>+</mo><msub><mi>a</mi><mn>n</mn></msub></mrow><mi>2</mi></mfrac></math> där <math><mi>n</mi></math> = antalet termer, <math><msub><mi>a</mi><mn>1</mn></msub></math> = det första talet i talföljden <math><msub><mi>a</mi><mn>n</mn></msub></math> = det sista talet i talföljden. Kontrollräkna programmets svar med hjälp av formeln.", "summa = 0\n")

    lesson5 = get_or_create_lesson(
        db,
        5,
        "If-satsen",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson5.md')
    )
    upsert_task(db, lesson5.id, 1, 1, "Skapa ett program som undersöker om ett tal är positivt. Om talet som användaren skriver in är större än 0 ska programmet skriva ut texten <q>Talet är positivt</q>. Om talet är 0 eller negativt ska ingenting hända.", "tal = float(input('Skriv ett tal: '))\n")
    upsert_task(db, lesson5.id, 2, 1, "Ett mattetest har 20 poäng som maximalt resultat. För att bli godkänd krävs det att eleven har minst 10 poäng. Skriv ett program som kollar poängen och skriver ut antingen <q>Godkänd</q> eller <q>Underkänd</q>.", "poang = int(input('Hur många poäng fick du på testet (0-20)? '))\n")
    upsert_task(db, lesson5.id, 3, 1, "Skriv ett program som tar emot två olika tal från användaren. Programmet ska jämföra talen och skriva ut vilket av talen som är störst, eller om de är exakt lika stora. Utskrifterna ska vara <q>Det första talet är störst</q>, <q>Det andra talet är störst</q> eller <q>Talen är lika stora</q>.", "tal1 = float(input('Skriv det första talet: '))\ntal2 = float(input('Skriv det andra talet: '))\n")
    upsert_task(db, lesson5.id, 4, 1, "Rent vatten fryser till is vid 0 °C eller kallare, och kokar (blir till gas) vid 100 °C eller varmare. Skriv ett program som tar emot en temperatur och avgör om vattnet är i <q>Fast form</q>, <q>Flytande form</q> eller <q>Gasform</q>.", "")
    upsert_task(db, lesson5.id, 5, 1, "Inom geometrin klassificeras vinklar efter sin storlek. Skriv ett program som frågar efter en vinkel i grader. Programmet ska svara om vinkeln är <q>Spetsig</q> (mindre än 90 grader), <q>Rät</q> (exakt 90 grader) eller <q>Trubbig</q> (större än 90 grader).", "")
    upsert_task(db, lesson5.id, 1, 2, "I matematiken kan en funktion ha olika regler för olika intervall. Skriv ett program som beräknar <math><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo></math> enligt följande regel:<ul><li><math><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mi>x</mi><mo>+</mo><mn>4</mn></math> om <math><mi>x</mi><mo>&lt;</mo><mn>2</mn></math></li><li><math><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mn>3</mn><mi>x</mi></math> om <math><mi>x</mi><mo>&ge;</mo><mn>2</mn></math></li></ul>", "")
    upsert_task(db, lesson5.id, 2, 2, "Skapa ett program som omvandlar provpoäng till ett betyg (A, C eller F) enligt dessa gränser:<ul><li>Minst 90 poäng ger ett A</li><li>Minst 50 poäng ger ett C</li><li>Mindre än 50 poäng ger ett F</li></ul><i>Tips: Tänk noga på i vilken ordning du testar villkoren! Om du kollar efter > 50 först, kommer någon med 95 poäng att fastna där och få ett C.</i>", "")
    upsert_task(db, lesson5.id, 3, 2, "När man löser en andragradsekvation med pq-formeln bestämmer värdet under roten (diskriminanten, <math><mi>D</mi></math>) hur många reella rötter ekvationen har.<ul><li>Om <math><mi>D</mi><mo>&gt;</mo><mn>0</mn></math> har ekvationen två reella rötter.</li><li>Om <math><mi>D</mi><mo>=</mo><mn>0</mn></math> har ekvationen en reell rot (dubbelrot).</li><li>Om <math><mi>D</mi><mo>&lt;</mo><mn>0</mn></math> saknas reella rötter.</li></ul>Enligt pq-formeln beräknas <math><mi>D</mi></math> som <math><mi>D</mi><mo>=</mo><msup><mrow><mo>(</mo><mfrac><mi>p</mi><mn>2</mn></mfrac><mo>)</mo></mrow><mn>2</mn></msup><mo>-</mo><mi>q</mi></math>. <br><br>Skriv ett program som tar emot värdet på <math><mi>p</mi></math> och <math><mi>q</mi></math> och skriver ut hur många rötter ekvationen har.", "")
    upsert_task(db, lesson5.id, 4, 2, "En bussbiljett har olika priser baserat på passagerarens ålder:<ul><li>Under 7 år: 0 kr (Gratis)</li><li>Under 20 år: 20 kr (Ungdom)</li><li>65 år eller äldre: 25 kr (Pensionär)</li><li>Alla andra: 35 kr (Vuxen)</li></ul>Skriv ett program som tar emot en ålder och skriver ut det korrekta biljettpriset.<br><br><i>Tips! Var noggrann med ordningen på dina if/elif/else!</i>", "")
    upsert_task(db, lesson5.id, 5, 2, "Du ska programmera en funktion med tre olika matematiska regler. Funktionen ser ut så här:<br><math><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mo>=</mo><mrow><mo>{</mo><mtable columnalign='left left' rowspacing='.2em' columnspacing='1em'><mtr><mtd><mo>&#x2212;</mo><mi>x</mi></mtd><mtd><mtext>om&#xA0;</mtext><mi>x</mi><mo>&lt;</mo><mo>&#x2212;</mo><mn>2</mn></mtd></mtr><mtr><mtd><msup><mi>x</mi><mn>2</mn></msup></mtd><mtd><mtext>om&#xA0;</mtext><mo>&#x2212;</mo><mn>2</mn><mo>&#x2264;</mo><mi>x</mi><mo>&#x2264;</mo><mn>5</mn></mtd></mtr><mtr><mtd><mn>25</mn></mtd><mtd><mtext>om&#xA0;</mtext><mi>x</mi><mo>&gt;</mo><mn>5</mn></mtd></mtr></mtable><mo></mo></mrow></math><br>Skriv ett program som beräknar <math><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo></math> om användaren matar in ett värde för <math><mi>x</mi></math>.<br><br><i>Tips! Var noggrann med ordningen på dina if/elif/else!</i>", "")

    lesson6 = get_or_create_lesson(
        db,
        6,
        "Utökade villkor",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson6.md')
    )
    upsert_task(db, lesson6.id, 1, 1, "Använd restoperatorn <code>%</code> för att kontrollera om ett heltal som användaren skriver in är jämnt eller udda. Om talet är jämnt ska programmet skriva ut <q>Talet är jämnt</q>, annars <q>Talet är udda</q>.", "tal = int(input('Skriv ett heltal: '))")
    upsert_task(db, lesson6.id, 2, 1, "Om ett tal är jämnt delbart med 5 blir resten 0 när man använder modulo 5 (<code>tal % 5 == 0</code>). Skriv ett program som kontrollerar om användarens tal ingår i 5:ans multiplikationstabell.", "")
    upsert_task(db, lesson6.id, 3, 1, "Du ska kontrollera om ett tal <math><mi>x</mi></math> ligger i det slutna intervallet mellan 10 och 20 (alltså <math><mn>10</mn><mo>&#x2264;</mo><mi>x</mi><mo>&#x2264;</mo><mn>20</mn></math>). Använd Pythons smarta mattegenväg (kedjad jämförelse) för att lösa uppgiften utan att använda ordet <code>and</code>. Utskrifterna kan vara <q>Inom intervallet</q> eller <q>Utanför intervallet</q>.", "")
    upsert_task(db, lesson6.id, 4, 1, "Ett mätinstrument kan bara mäta temperaturer mellan 0 °C och 100 °C. Om temperaturen är under 0 ELLER över 100 är värdet ogiltigt. Skriv ett program som använder <code>or</code> för att varna om temperaturen är ogiltig.", "")
    upsert_task(db, lesson6.id, 5, 1, "För att få betyg C på ett nationellt prov krävs det att poängen ligger i intervallet <math><mo>[</mo><mn>60</mn><mo>,</mo><mn>79</mn><mo>]</mo></math>, det vill säga minst 60 poäng men högst 79 poäng. Skriv ett program som kollar om elevens poäng räcker till exakt ett C (varken mer eller mindre).", "")
    upsert_task(db, lesson6.id, 1, 2, "Ett tal som är jämnt delbart med både 2 och 3 är också delbart med 6. Skriv ett program som använder <code>%</code> och <code>and</code> för att kontrollera om ett tal är jämnt delbart med både 2 och 3.", "")
    upsert_task(db, lesson6.id, 2, 2, "För att tre vinklar ska kunna bilda en triangel måste två matematiska villkor vara uppfyllda samtidigt:<ol><li>Vinkelsumman måste vara exakt 180 grader.</li><li>Alla tre vinklar måste vara större än 0 grader.</li></ol>Skriv ett program som kontrollerar om tre inmatade triangelvinklar uppfyller kraven.", "v1 = float(input('Vinkel 1: '))\nv2 = float(input('Vinkel 2: '))\nv3 = float(input('Vinkel 3: '))\n")
    upsert_task(db, lesson6.id, 3, 2, "I ett koordinatsystem har vi en kvadrat. För att en punkt <math><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo></math> ska ligga inuti kvadraten måste <math><mi>x</mi></math>-koordinaten ligga mellan 0 och 5 (<math><mn>0</mn><mo>&#x2264;</mo><mi>x</mi><mo>&#x2264;</mo><mn>5</mn></math>) SAMTIDIGT som <math><mi>y</mi></math>-koordinaten ligger mellan 0 och 5 (<math><mn>0</mn><mo>&#x2264;</mo><mi>y</mi><mo>&#x2264;</mo><mn>5</mn></math>). Skriv ett program som kontrollerar om punkten är inuti kvadraten. Hur ser kvadraten ut?", "")
    upsert_task(db, lesson6.id, 4, 2, "I ett mattespel är ett tal <q>magiskt</q> om det uppfyller två krav:<ol><li>Det måste vara ett udda tal.</li><li>Det måste vara jämnt delbart med antingen 3 eller 7.</li></ol>Skriv ett program som kontrollerar om ett tal är magiskt.<br><br><i>Tips: Du kan använda parenteser i Python för att gruppera villkor, precis som i matematiken, till exempel: <code>villkor1 and (villkor2 or villkor3)</code>.</i>", "")
    upsert_task(db, lesson6.id, 5, 2, "Att räkna ut om ett år är ett skottår är en klassisk programmeringsutmaning som kräver skarp logik. Reglerna är:<ul><li>Året måste vara jämnt delbart med 4.</li><li><strong>MEN</strong> om året är delbart med 100 är det inte ett skottår, <strong>SÅVIDA</strong> det inte också är jämnt delbart med 400.</li></ul>Skriv ett program som kontrollerar om ett år är ett skottår eller inte.<br><br>Testa din logik ordentligt! (Exempel: 2000 var skottår, 1900 var det inte, 2024 var det)", "")

    lesson7 = get_or_create_lesson(
        db,
        7,
        "While-satsen",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson7.md')
    )
    upsert_task(db, lesson7.id, 1, 1, "Skapa en while-loop som skriver ut talen från 1 till 10. Kom ihåg att öka räknarvariabeln <code>i</code> med 1 inuti loopen så att den inte fortsätter för evigt!", "i = 1\n\nwhile ")
    upsert_task(db, lesson7.id, 2, 1, "Skapa en nedräkning för en raket. Loopen ska starta på 5 och räkna nedåt till 1. Använd en while-loop. Efter att loopen är helt klar ska programmet skriva ut <q>Liftoff!</q>.", "")
    upsert_task(db, lesson7.id, 3, 1, "Starta med talet 1. Skapa en while-loop som multiplicerar talet med 2 (dubblerar det) så länge som talet är mindre än 100. Skriv ut talet för varje varv.", "")
    upsert_task(db, lesson7.id, 4, 1, "Skriv ett program som ber användaren skriva in ett tal. Programmet ska fortsätta fråga efter nya tal om och om igen, ända tills användaren skriver in siffran 0. Då ska loopen avslutas. Skriv ut <q>Programmet avslutades</q> sist i programmet så att du ser att det är klart.", "")
    upsert_task(db, lesson7.id, 5, 1, "Starta med talet 500. Skapa en while-loop som dividerar talet med 3 så länge som talet är större än 5. Använd en räknare (<code>steg</code>) för att räkna hur många divisioner som krävdes och skriv ut det efter loopen.", "")
    upsert_task(db, lesson7.id, 1, 2, "Skapa en evig loop med <code>while True:</code>. Inuti loopen ska programmet fråga efter ett lösenord. Om användaren skriver <q>matte4life</q> ska programmet använda <code>break</code> för att bryta loopen och hälsa välkommen. Annars ska det säga <q>Fel lösenord</q> och fråga igen.", "")
    upsert_task(db, lesson7.id, 2, 2, "Du har 500 kr på ett sparkonto. Varje månad sparar du ytterligare 150 kr. Du vill köpa en dator som kostar 5 000 kr. Skapa en while-loop som räknar ut hur många månader du måste spara innan du har råd med datorn.", "")
    upsert_task(db, lesson7.id, 3, 2, "Du ska skriva ett program som dividerar talet 100 med ett tal <math><mi>x</mi></math> som användaren får välja. Eftersom division med noll är odefinierat inom matematiken, måste vi se till att användaren inte råkar skriva in 0. <br><br>Använd <code>while True:</code> och skapa en loop som fortsätter så länge användaren skriver in 0. Så fort de skriver in ett godkänt tal (alltså ett tal som inte är lika med 0) ska loopen avbrytas med <code>break</code>. Därefter ska programmet beräkna och skriva ut resultatet.", "")
    upsert_task(db, lesson7.id, 4, 2, "En matematisk talföljd startar på 1. Nästa tal i den här talföljden beräknas alltid genom att ta det förra talet, multiplicera med 2 och sedan lägga till 1. Skriv en while-loop som genererar och skriver ut alla tal i denna följd så länge talen är mindre än 200.<br><br>(Följden ska starta: 1, 3, 7, 15...)", "")
    upsert_task(db, lesson7.id, 5, 2, "Detta är ett av matematikens mest kända olösta problem (även kallat <math><mi>3x</mi><mo>+</mo><mi>1</mi></math>-problemet). Man väljer ett starttal och följer dessa regler:<ul><li>Om talet är jämnt: Dela talet med 2.</li><li>Om talet är udda: Multiplicera med 3 och lägg till 1.</li></ul>Om man upprepar detta verkar det som att man alltid till slut hamnar på talet 1. Skriv en while-loop som fortsätter så länge <code>tal != 1</code>. Räkna hur många steg (varv) som krävs innan programmet når 1!", "")

    lesson8 = get_or_create_lesson(
        db,
        8,
        "Exponentiell tillväxt",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson8.md')
    )
    upsert_task(db, lesson8.id, 1, 1, "Du sätter in 5 000 kr på ett konto med en årlig ränta på 3% (förändringsfaktor 1.03). Skriv en for-loop som beräknar och skriver ut kapitalet år för år under totalt 10 år.", "kapital = 5000\nforandringsfaktor = 1.03\n\n# Skriv en for-loop som körs 10 gånger (för år 1 till 10)\nfor ar in range(1, 11):\n    # Räkna ut det nya kapitalet och skriv ut resultatet")
    upsert_task(db, lesson8.id, 2, 1, "I ett biologiskt experiment startar man med 100 bakterier. Antalet bakterier fördubblas varje timme (förändringsfaktor 2). Använd en for-loop för att simulera och skriva ut antalet bakterier varje timme under de första 6 timmarna.", "bakterier = 100\n\n# Skriv en for-loop som körs 6 gånger")
    upsert_task(db, lesson8.id, 3, 1, "Exponentialfunktioner kan också beskriva en minskning. En ny bil köps för 250 000 kr. Värdet minskar med 15% varje år, vilket ger förändringsfaktorn 0.85 (100%-15%=85%). Skriv ett program som beräknar bilens värde efter 5 år.", "bilvarde = 250000\nfaktor = 0.85\n\n# Använd en for-loop för att räkna ut värdet efter 5 år\n\nprint('Efter 5 år är bilen värd', round(bilvarde), 'kr.')")
    upsert_task(db, lesson8.id, 4, 1, "På grund av övergödning ökar arean av en algmatta i en sjö med 20% varje dag. Från början täcker algerna en area på 2 m<sup>2</sup>. Skriv en loop som skriver ut algmattans area dag för dag under en vecka (7 dagar).", "area = 2\n\n# Skriv en for-loop för 7 dagar")
    upsert_task(db, lesson8.id, 5, 1, "Nu vänder vi på problemet! Du startar med 10 000 kr på ett konto med 5% ränta. Du vill veta hur många år det tar innan du har minst 15 000 kr. Använd en while-loop och en räknare för år.", "kapital = 10000\nranta = 1.05\nar = 0  # Vår tidsräknare (x-värdet)\n\n# Loopen ska fortsätta så länge kapitalet är MINDRE än 15000\nwhile kapital < 15000:\n    # Öka kapitalet med räntan\n    Öka årsräknaren med 1\n\nprint('Det tar', ar, 'år innan kapitalet har nått 15 000 kr.')")
    upsert_task(db, lesson8.id, 1, 2, "I ett förråd har det kommit in flugor. De är 50 stycken från början och antalet ökar med 30% varje vecka. Skriv en while-loop som räknar ut hur många veckor det tar innan det finns över 1 000 flugor i förrådet.", "flugor = \nfaktor = \nveckor = \n\n# Skriv din while-loop här")
    upsert_task(db, lesson8.id, 2, 2, "Ett radioaktivt ämne sönderfaller (minskar) exponentiellt. Från början har vi ett prov på 80 gram. Varje år försvinner 12% av ämnet. Skriv en while-loop som räknar ut hur många år det tar innan det finns mindre än 10 gram kvar av ämnet.", "massa = \nfaktor = \nar = \n\n# Loopa så länge massan är större än 10 gram")
    upsert_task(db, lesson8.id, 3, 2, "På grund av inflation och dåliga skördar ökar priset på ett kaffepaket med 4% varje år. Idag kostar paketet 45 kr. Skriv ett program som räknar ut efter hur många år kaffepaketet kommer att kosta mer än 80 kr.", "pris = \ninflation = \nar = \n\n# Skriv din while-loop här")
    upsert_task(db, lesson8.id, 4, 2, "Två personer sparar pengar på olika sätt och startar med 5 000 kr var. <ul><li>Kalle (linjär ökning): Sätter in exakt 1 500 kr i kontanter i ett kassaskåp varje år.</li><li>Stina (exponentiell ökning): Sätter in sina pengar i en aktiefond som i snitt ökar med 10% i värde varje år, men gör inga nya insättningar.</li></ul>I början kommer Kalle att ha mer pengar eftersom han sätter in nya pengar, men efter ett tag kommer Stinas exponentiella tillväxt att springa förbi. Skriv en while-loop som tar reda på efter hur många år Stina har mer pengar än Kalle.", "kalle = \nstina = \nar = \n\n# Så länge Kalle har mer eller lika mycket pengar som Stina, fortsätt loopen\n\n    # Uppdatera Kalles pengar\n    # Uppdatera Stinas pengar\n    # Öka årsräknaren\n\nprint('Efter', ar, 'år har Stina gått om Kalle!')\nprint('Kalle har då:', round(kalle), 'kr. Stina har:', round(stina), 'kr.')")
    upsert_task(db, lesson8.id, 5, 2, "Inom fysik och matematik talar man om halveringstid – alltså den tid det tar för en mängd att minska till hälften av vad det var från början.<br><br>Ett instabilt grundämne väger från början 1 000 gram. Varje minut sönderfaller ämnet så att dess massa minskar med 5%. Skriv ett program som använder en while-loop för att ta reda på ämnets halveringstid.", "start_massa = \nmassa = start_massa\nfaktor = \nminuter = \n\n# Loop för att ta reda på halveringstiden")

    lesson9 = get_or_create_lesson(
        db,
        9,
        "Listor",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson9.md')
    )
    upsert_task(db, lesson9.id, 1, 1, "Skapa ett program som innehåller en lista med fem olika provresultat (poäng). Använd den inbyggda funktionen <code>len()</code> för att ta reda på och skriva ut hur många provresultat som finns sparade i listan.", "poang = [14, 22, 18, 25, 19]\n\n# Använd len() för att ta reda på antalet element och spara i en variabel\nantal = \n\nprint('Listan innehåller', antal, 'stycken provresultat.')")
    upsert_task(db, lesson9.id, 2, 1, "Du har en lista som håller reda på temperaturer under en vecka. En ny dag har passerat och du vill lägga till måndagens temperatur, som var 16.5 grader, sist i listan. Använd funktionen <code>.append()</code> för att göra detta.", "temperaturer = [12.1, 14.3, 15.0, 13.8]\n\n# Använd .append() för att lägga till 16.5 i listan temperaturer\n\nprint('Den uppdaterade listan är:', temperaturer)")
    upsert_task(db, lesson9.id, 3, 1, "Inom statistiken är det viktigt att hitta det största och minsta värdet (extremvärdena). Skriv ett program som använder de färdiga funktionerna <code>max()</code> och <code>min()</code> för att hitta det högsta respektive lägsta resultatet i en lista över tider (i sekunder).", "tider = [65.2, 58.8, 71.3, 62.1, 59.5, 64.0]\n\n# Hitta minsta och största värdet med min() och max()\nsnabbast = \nlangsammast = \n\nprint('Den snabbaste tiden var', snabbast, 'sekunder.')\nprint('Den långsammaste tiden var', langsammast, 'sekunder.')")
    upsert_task(db, lesson9.id, 4, 1, "En elev sparar pengar i en burk varje vecka. Listan nedan visar hur många kronor eleven har lagt i burken per vecka. Använd funktionen <code>sum()</code> för att räkna ut hur mycket pengar som finns i burken totalt.", "sparande = [50, 20, 100, 40, 50, 75]\n\n# Använd sum() för att räkna ut den totala summan\n\nprint('Eleven har sparat totalt', totalt, 'kr.')")
    upsert_task(db, lesson9.id, 5, 1, "Skriv ett program som beräknar medelhöjden för sex plantor i ett biologiskt experiment. Använd de färdiga funktionerna <code>sum()</code> och <code>len()</code> för att bygga formeln för medelvärde.", "hojder_cm = [12.5, 14.2, 11.8, 15.0, 13.1, 16.4]\n\n# 1. Räkna ut summan och antalet med sum() och len()\n\n# 2. Beräkna medelvärdet\n\nprint('Plantornas medelhöjd är', round(medelvärde, 1), 'cm.')")
    upsert_task(db, lesson9.id, 1, 2, "Du har fått i uppdrag att analysera vikten på sju nyfödda kattungar. Skriv ett program som skriver ut tre saker: den lättaste kattungens vikt, den tyngsta kattungens vikt samt kattungarnas medelvikt.", "vikter_gram = [98, 105, 87, 112, 101, 94, 102]\n\n# Skriv koden som hittar min, max och beräknar medelvärdet")
    upsert_task(db, lesson9.id, 2, 2, "Du har genomfört ett sannolikhetsexperiment där du singlat slant 10 gånger. Krona har registrerats som 1 och klave som 0. Använd funktionen <code>.count()</code> för att ta reda på den absoluta frekvensen för krona (det vill säga hur många gånger siffran 1 förekommer i listan).", "slant_kast = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]\n\n# Räkna antalet ettor\nantal_krona = \n\nprint('Absolut frekvens för krona:', antal_krona, 'gånger.')")
    upsert_task(db, lesson9.id, 3, 2, "En tärning har kastats ett antal gånger och resultaten har sparats i en lista. Skriv ett program som beräknar den relativa frekvensen (den experimentella sannolikheten) för att få en 5:a.<br><br>Formel: <math><mi>Relativ frekvens</mi><mo>=</mo><mfrac><mrow>Antal gynnsamma utfall (femmor)</mrow><mrow>Totalt antal utfall (kast)}</mrow></mfrac></math>", "kast = [5, 3, 2, 5, 6, 1, 4, 5, 2, 3, 5, 6]\n\n# 1. Räkna hur många femmor som finns i listan\nantal_femmor = \n\n# 2. Ta reda på totalt antal kast i listan\ntotalt_kast = \n\n# 3. Beräkna den relativa frekvensen\nrel_frekvens = \n\nprint('Den experimentella sannolikheten för en 5:a är', round(rel_frekvens * 100, 1), '%')")
    upsert_task(db, lesson9.id, 4, 2, "Du har en värdetabell för en bilresa där <math><mi>x</mi></math> är tid i timmar och <math><mi>y</mi></math> är bilens totala sträcka i kilometer. Skriv ett program som använder <code>matplotlib.pyplot</code> för att rita ett linjediagram över resan. Lägg till en titel, namnge axlarna och aktivera rutnätet (<code>plt.grid(True)</code>).", "import matplotlib.pyplot as plt\n\n# Värdetabell sparad i två listor\ntid_timmar = [0, 1, 2, 3, 4]\nstracka_km = [0, 80, 150, 240, 310]\n\nplt.clf()\n\n# 1. Använd plt.plot() för att skapa grafen\n\n# 2. Lägg till titel, xlabel, ylabel och grid\n\n# 3. Visa grafen\nplt.show()")
    upsert_task(db, lesson9.id, 5, 2, "Du ska visualisera <math><mi>y</mi><mo>=</mo><msup><mi>x</mi><mn>3</mn></msup><mo>-</mo><mn>4</mn><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><mn>5</mn></math> genom att rita dess graf med hjälp av uträknade värden. Du kan göra det i intervallet [-5, 5] med steget 0,1. Gör diagrammet rött men ha ingen marker genom att lägga till parametern <code>color='red'</code> inuti din <code>plt.plot()</code>-funktion.", "# Importera plot- och matteverktygen\nimport matplotlib.pyplot as plt\nimport numpy as np\n\n# Vår värdetabell uppdelad i x- och y-värden\nx_varden = np.arange( )\ny_varden = [   for x in x_varden]\n\n# 1. Skapa själva grafen utifrån listorna\n\n# 2. Snygga till koordinatsystemet med rubriker och rutnät\n\n# 3. Visa fönstret med grafen")

    lesson10 = get_or_create_lesson(
        db,
        10,
        "Slumptal",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson10.md')
    )
    upsert_task(db, lesson10.id, 1, 1, "För att använda slumptal i Python måste vi importera modulen random. Funktionen <code>random.randint(a, b)</code> ger ett slumpmässigt heltal mellan <math><mi>a</mi></math> och <math><mi>b</mi></math> (inklusive gränserna). Skriv ett program som simulerar ett kast med en vanlig sexsidig tärning och skriver ut resultatet.", "import random\n\n# Generera ett slumptal mellan 1 och 6\nresultat = \n\nprint('Du slog en:', resultat)")
    upsert_task(db, lesson10.id, 2, 1, "Skriv ett program som simulerar att du kastar två sexsidiga tärningar samtidigt. Programmet ska spara kasten i två olika variabler, räkna ut summan av dem och skriva ut resultatet.", "import random\n\n# Simulera två olika tärningskast\ntarning1 = \ntarning2 = \n\n# Beräkna summan\nsumma = \n\nprint('Tärningarna visade', tarning1, 'och', tarning2, '. Summan är', summa, '.')")
    upsert_task(db, lesson10.id, 3, 1, "Skapa ett program som innehåller en lista med de tre alternativen <q>Sten</q>, <q>Sax</q> och <q>Påse</q>. Använd <code>random.choice()</code> för att låta datorn slumpa fram sitt drag i spelet och skriv ut resultatet på skärmen.", "import random\n\n# En lista med de tre möjliga valen\nalternativ = ['Sten', 'Sax', 'Påse']\n\n# Använd random.choice() för att välja ett slumpmässigt föremål från listan\ndatorns_val = \n\nprint('Datorn väljer:', datorns_val)")
    upsert_task(db, lesson10.id, 4, 1, "Kombinera slumptal med en loop! Skriv ett program som använder en for-loop för att kasta en sexsidig tärning exakt 10 gånger. Varje kast ska skrivas ut på skärmen.", "import random\n\n# Skriv en for-loop som körs 10 gånger\nfor i in range(  ):\n    # Slumpa och skriv ut tärningskastet")
    upsert_task(db, lesson10.id, 5, 1, "Detta är det klassiska exemplet på när vi inte vet antalet varv i förväg. Skapa en while-loop som fortsätter att kasta en tärning om och om igen så länge resultatet <strong>inte</strong> är en 6:a. Använd en räknare för att hålla reda på hur många kast som krävdes.", "import random\n\ntarning = 0\nkast = 0\n\n# Loopen ska köra så länge tärningen INTE är 6\nwhile \n    tarning = \n    # Öka kasträknaren med 1\n\n    print('Kast', kast, ': en', tarning, ':a')\n\nprint('Det krävdes', kast, 'kast för och få en 6:a!')")
    upsert_task(db, lesson10.id, 1, 2, "Skriv ett program som simulerar 20 tärningskast och sparar alla resultat i en lista med hjälp av <code>.append()</code>. Använd sedan listfunktionen <code>.count()</code> för att ta reda på den absoluta frekvensen (hur många gånger du fick en 6:a under dessa 20 kast).", "import random\n\nresultat_lista = []\n\n# 1. Skapa en loop som körs 20 gånger och lägger till slumptal i listan\n\n# 2. Räkna antalet sexor med .count()\nantal_sexor = \n\nprint('Alla kast:', resultat_lista)\nprint('Antal sexor:', antal_sexor)")
    upsert_task(db, lesson10.id, 2, 2, "Enligt sannolikhetsläran är den teoretiska sannolikheten för att få krona vid en slantsingling 50% (0.5). Ju fler gånger vi utför experimentet, desto närmare 0.5 bör den relativa frekvensen komma.<br><br>Skriv ett program som simulerar en slantsingling (0 eller 1) många gånger. Testa med 100, 1 000, 10 000 osv. Räkna hur många gånger det blev krona (1) och räkna ut den experimentella sannolikheten: <math><mfrac><mrow>Antal krona</mrow><mrow>Antal kast</mrow></mfrac></math>.", "import random\n\nantal_krona = \nantal_kast = \n\nfor i in range(   ):\n    slant = \n    if slant == 1:\n        antal_krona = \n\n# Beräkna den relativa frekvensen (experimentell sannolikhet)\nsannolikhet = \n\nprint('Efter', antal_kast, 'kast blev det krona', antal_krona, 'gånger.')\nprint('Experimentell sannolikhet:', sannolikhet, '(teoretisk är 0.5)')")
    upsert_task(db, lesson10.id, 3, 2, "När man kastar två tärningar är 7 den absolut vanligaste summan (det finns 6 olika sätt att få summan 7 på totalt 36 kombinationer, vilket ger en teoretisk sannolikhet på <math><mfrac><mrow>6</mrow><mrow>36</mrow></mfrac><mo>&asymp;</mo><mn>16.7</mn><mo>%</mo></math>). Skriv ett program som kastar två tärningar 1 000 gånger. Räkna hur många gånger summan blir exakt 7 och beräkna den experimentella sannolikheten i procent.", "import random\n\nantal_sjuor = \n\n# Skapa en loop som körs 1000 gånger\n# Inuti loopen: Slumpa två tärningar, addera och kolla om summan är 7\n\nprocent = \n\nprint('Det blev summan sju i', procent, '% av fallen.')")
    upsert_task(db, lesson10.id, 4, 2, "Skapa ett klassiskt spel! Låt datorn slumpa ett hemligt tal mellan 1 och 100 innan loopen startar. Skapa sedan en evig loop (<code>while True:</code>) där användaren får gissa talet.<ul><li>Om gissningen är för låg, ska datorn skriva <q>Högre!</q>.</li><li>Om gissningen är för hög, ska datorn skriva <q>Lägre!</q>.</li><li>Om gissningen är rätt, ska loopen avbrytas med <code>break</code> och spelet är slut.</li></ul>", "import random\n\nhemligt_tal = \n\nprint('Jag tänker på ett tal mellan 1 och 100. Gissa vilket!')\n\n# Loopa för evigt\n    gissning = \n\n    # Skriv dina if-elif-else-satser här för att ge ledtrådar eller köra break")
    upsert_task(db, lesson10.id, 5, 2, "Inom matematiken och fysiken studerar man ofta något som kallas Random Walk (slumpmässig vandring). Tänk dig att en partikel startar i punkten 0 på en tallinje. Partikeln tar totalt 100 steg. För varje steg singlar vi slant:<ul><li>Om det blir krona (1) tar partikeln ett steg till höger.</li><li>Om det blir klave (0) tar partikeln ett steg till vänster.</li></ul>Skriv ett program som simulerar partikelns 100 steg och skriver ut vilken position på tallinjen partikeln befinner sig på till slut.<br><br>Kör programmet flera gånger för att se hur mycket slutpositionen varierar!", "import random\n\nposition = 0\n\n# Skriv en loop som körs 100 gånger\n# Varje varv simulerar en slantsingling som antingen ökar eller minskar positionen\n\nprint('Efter 100 slumpmässiga steg hamnade partikeln på position:', position)")

    lesson11 = get_or_create_lesson(
        db,
        11,
        "Nästlade for-satser",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson11.md')
    )
    upsert_task(db, lesson11.id, 1, 1, "För att förstå hur nästlade loopar fungerar ska vi rita ett enkelt rutnät av plustecken (+). Den yttre loopen bestämmer hur många rader vi gör, och den inre loopen bestämmer hur många kolumner (plustecken per rad) vi skriver ut.<br><br>Skapa ett program som ritar ett rutnät med 3 rader och 4 plustecken på varje rad.<br><br>Testa att variera antalet rader och kolumner, så du är säker på hur nästlade loopar fungerar.", "# Den yttre loopen styr raderna (3 stycken)\nfor rad in range(   ):\n    # Den inre loopen styr kolumnerna (4 stycken)\n    for kolumn in range(   ):\n        # end=' ' gör att datorn inte byter rad efter varje plustecken\n        print('+', end=' ')\n\n    # När en hel rad är klar gör vi ett radbyte innan nästa varv i yttre loopen\n    print()")
    upsert_task(db, lesson11.id, 2, 1, "Inom sannolikhetslära vill vi ofta lista alla möjliga kombinationer. Tänk dig att du kastar två tärningar som bara har 3 sidor var (siffrorna 1, 2 och 3). Använd nästlade loopar för att skriva ut alla möjliga par av resultat.", "# Den yttre loopen är första tärningen (1 till 3)\nfor tarning1 in range(   ):\n    # Den inre loopen är andra tärningen (1 till 3)\n    for tarning2 in range(   ):\n        print('Tärning 1:', tarning1, '  Tärning 2:', tarning2)")
    upsert_task(db, lesson11.id, 3, 1, "Multiplikationstabellen är det ultimata exemplet på en nästlad struktur. Skriv ett program som använder två loopar (som båda går från 1 till 5) för att beräkna och skriva ut produkten av loopvariablerna.", "# Yttre loop för tal 1 till 5\nfor i in range(   ):\n    # Inre loop för tal 1 till 5\n    for j in range(   ):\n        produkt = \n        print(i, '*', j, '=', produkt)")
    upsert_task(db, lesson11.id, 4, 1, "I matematiken ritar vi ofta i ett koordinatsystem. Vi kan låta den yttre loopen representera <math><mi>x</mi></math>-axeln och den inre loopen representera <math><mi>y</mi></math>-axeln. Skriv ett program som genererar och skriver ut alla heltalskoordinater <math><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo></math> där både <math><mi>x</mi></math> och <math><mi>y</mi></math> går från 0 till 3.", "# x går från 0 till 3\nfor x in range(   ):\n    # y går från 0 till 3\n    for y in range(   ):\n        # Skriv ut koordinaten på formen (x, y)")
    upsert_task(db, lesson11.id, 5, 1, "Skriv ett program som använder nästlade loopar för att gå igenom alla 36 möjliga kombinationer för två vanliga sexsidiga tärningar (1 till 6). Programmet ska för varje kombination beräkna och skriva ut summan.", "# Loopa tärning 1 från 1 till 6\nfor t1 in range(   ):\n    # Loopa tärning 2 från 1 till 6\n    for t2 in range(   ):\n        # Beräkna summan och skriv ut (t.ex. Tärningarna 2 och 4 ger summan 6)")
    upsert_task(db, lesson11.id, 1, 2, "Nu bygger vi vidare på tärningarna! Istället för att bara skriva ut summorna ska vi använda en räknare för att ta reda på den teoretiska sannolikheten för att få summan 7.<br><br>Låt looparna gå igenom alla 36 kombinationer. Använd en if-sats inuti den inre loopen för att kontrollera om summan blir 7. Om den blir det, öka din räknare med 1. Beräkna till slut sannolikheten genom att dela antalet sjuor med 36.", "antal_sjuor = 0\ntotala_kombinationer = 36\n\n# Skapa de nästlade looparna för de två tärningarna\n# Inuti den inre loopen: kolla if-sats för summan\n\nsannolikhet = \n\nprint('Antal sätt att få summan 7:', antal_sjuor)\nprint('Teoretisk sannolikhet:', round(sannolikhet*100, 1), '%')")
    upsert_task(db, lesson11.id, 2, 2, "Vi kan göra den inre loopen beroende av den yttre loopen. Om den yttre loopen har variabeln <code>rad</code>, kan den inre loopen köra <code>range(rad + 1)</code> gånger. På så sätt blir varje ny rad en stjärna längre än den förra, och vi får en rätvinklig triangel!<br><br>Skriv ett program som ritar en triangel som är 5 rader hög.", "# rad kommer att ha värdena 0, 1, 2, 3, 4\nfor rad in range(   ):\n    # Den inre loopen körs olika många gånger beroende på vilken rad vi är på\n    for kolumn in range(rad + 1):\n        print('*', end=' ')\n    print() # Radbyte efter varje färdig rad")
    upsert_task(db, lesson11.id, 3, 2, "Inom programmering innebär <i>brute force</i> att man låter datorn testa precis alla möjliga kombinationer för att hitta rätt svar. Det här är ett kraftfullt verktyg i matematik för att hitta heltalslösningar till ekvationer med flera variabler.<br><br>Du ska lösa den diofantiska ekvationen: <math><mn>3</mn><mi>x</mi><mo>+</mo><mn>2</mn><mi>y</mi><mo>=</mo><mn>24</mn></math>. Skriv ett program med nästlade for-satser där både <math><mi>x</mi></math> och <math><mi>y</mi></math> testas för alla heltal från 0 till 10. Inuti den inre loopen lägger du en if-sats som kontrollerar om <math><mn>3</mn><mi>x</mi><mo>+</mo><mn>2</mn><mi>y</mi><mo></math> blir exakt lika med 24. Om det stämmer har datorn hittat en lösning, och ska då skriva ut lösningen.", "print('Söker efter heltalslösningar till 3x + 2y = 24...')\n\n# Loopa x från 0 till 10\nfor x in range(   ):\n    # Loopa y från 0 till 10\n    for y in range(   ):\n        # Skriv en if-sats som kontrollerar om ekvationen är sann\n            print('Hittade en lösning: x =', x, ', y = ', y)")
    upsert_task(db, lesson11.id, 4, 2, "Inom kombinatoriken vill vi ibland välja ut par av tal där ordningen inte spelar någon roll. Om vi väljer paret (1, 2) vill vi inte ha med (2, 1) eftersom det är samma siffror. Vi vill inte heller ha (1, 1) eftersom det måste vara två olika tal.<br><br>Ett smart trick är att låta den inre loopen starta på <code>x + 1</code> istället för på 0. Då blir <math><mi>y</mi></math> alltid större än <math><mi>x</mi></math>, och vi slipper dubbletter. Skriv ett program som listar alla unika par ur talen 0, 1, 2 och 3.<br><br>När du har fått paren att fungera kan du använda samma teknik till att välja vilka två färger du ska matcha. Skapa en lista med färger, till exempel <code>farger = ['brun', 'blå', 'grön', 'röd']</code>. Skriv sedan ut färgerna på indexen <code>x</code> och <code>y</code> i stället för talen.", "# Yttre loop för x (0 till 3)\nfor x in range(   ):\n    # Inre loop för y startar på x + 1 för att undvika dubbletter\n    for y in range(   ):\n        print('Par: (', x, ',', y, ')')")
    upsert_task(db, lesson11.id, 5, 2, "Detta är en klassisk matematisk metod för att uppskatta areor (liknande Monte Carlo-metoden). Cirkelns ekvation säger att alla punkter <math><mo>(</mo><mi>x</mi><mo>,</mo><mi>y</mi><mo>)</mo></math> som uppfyller <math><mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><msup><mi>y</mi><mn>2</mn></msup><mo>&le;</mo><msup><mi>r</mi><mn>2</mn></msup></mrow></math> ligger inuti en cirkel med radien <math><mi>r</mi></math> som har sitt centrum i origo (0,0).<br><br>Tänk dig att vi undersöker den första kvadranten där <math><mi>x</mi></math> går från 0 till 5 och <math><mi>y</mi></math> går från 0 till 5. Skriv ett program som med nästlade loopar undersöker alla dessa 36 punkter och räknar hur många av dem som ligger inuti eller på en cirkel med radien <math><mi>r</mi><mo>=</mo><mn>5</mn></math> (det vill säga där <math><mrow><msup><mi>x</mi><mn>2</mn></msup><mo>+</mo><msup><mi>y</mi><mn>2</mn></msup><mo>&le;</mo><mn>25</mn></mrow></math>).<img src='/illustrations/punkter-i-cirkel.png' alt='Graf över punkter i kvartscirkel' class='task-image'>", "punkter_i_cirkel = 0\n\n# Loopa igenom x och y från 0 till 5\nfor x in range(   ):\n    for y in range(   ):\n        # Räkna ut x^2 + y^2\n        varde = \n\n        # Kontrollera om punkten ligger inom cirkeln (varde <= 25)\n\nprint('Antal heltalspunkter inuti cirkelsektorn:', punkter_i_cirkel)")

    lesson12 = get_or_create_lesson(
        db,
        12,
        "Turtle-grafik",
        markdown_file=os.path.join(BASE_DIR, 'content', 'lessons', 'lesson12.md')
    )
    upsert_task(db, lesson12.id, 1, 1, "Starta med grunderna! I de här uppgifterna jobbar du i Thonny. Klistra gärna in dina lösningar i kodrutorna här när varje uppgift är klar.<br><br>Importera turtle och skapa en sköldpadda. Skriv ett program som ritar ett enkelt trappsteg. Sköldpaddan ska gå framåt 50 steg, svänga 90 grader åt höger, och sedan gå framåt 50 steg till.", "import turtle\n\nt = turtle.Turtle()  # Skapar sköldpaddan t\n\n# Skriv kod så att t går framåt, svänger höger och går framåt igen\nt.forward(50)\n\n# Håller fönstret öppet när sköldpaddan är klar\nturtle.done()")
    upsert_task(db, lesson12.id, 2, 1, "I stället för att skriva samma instruktioner om och om igen ska du använda en for-loop. Skapa en loop som körs 4 gånger för att rita en perfekt kvadrat med sidlängden 100.", "import turtle\n\nt = turtle.Turtle()\n\n# Skapa en for-loop som körs 4 gånger\nfor i in range(   ):\n    # Gå framåt 100 och sväng 90 grader åt vänster eller höger\n\nturtle.done()")
    upsert_task(db, lesson12.id, 3, 1, "En romb är en geometrisk fyrhörning där alla sidor är lika långa, men hörnen är inte rätvinkliga (90°). I stället växlar vinklarna! För att formen ska sluta sig använder vi sidovinklar (som tillsammans blir 180°). Om den första svängen är en yttervinkel på 60°, måste nästa sväng vara en yttervinkel på 180° - 60° = 120°.<br><br>Skriv en for-loop som körs 2 gånger. Inuti loopen ska sköldpaddan rita två sidor: först gå framåt och svänga 60 grader, och sedan gå framåt lika långt och svänga 120 grader.<br><br>När du har fått det att fungera kan du prova med andra vinklar i romben.", "import turtle\n\nt = turtle.Turtle()\n\n# Skapa en loop som körs 2 gånger\nfor i in range(   ):\n    # 1. Gå framåt 100 steg och sväng 60 grader åt vänster\n\n    # 2. Gå framåt 100 steg och sväng 120 grader åt vänster\n\nturtle.done()")
    upsert_task(db, lesson12.id, 4, 1, "Skapa ett program som ritar en rektangel. Använd två variabler: <code>bredd = 150</code> och <code>hojd = 75</code>. Genom att använda variabler blir det lätt att ändra storlek på hela rektangeln i efterhand.", "import turtle\n\nt = turtle.Turtle()\n\nbredd = 150\nhojd = 75\n\n# Rita rektangeln genom att växla mellan att använda 'bredd' och 'hojd'\n# Tips: Du kan använda en loop som körs 2 gånger!\n\nturtle.done()")
    upsert_task(db, lesson12.id, 5, 1, "Inom datorgrafik finns det egentligen inga <q>perfekta</q> cirklar, utan datorn ritar istället en månghörning med så många och korta sidor att det ser ut som en cirkel för det mänskliga ögat. Detta kallas för att approximera en cirkel.<br><br>Ett helt varv är som bekant 360°. Om vi skapar en loop som körs hela 360 gånger, där sköldpaddan bara går 2 steg framåt och sedan svänger exakt 1 grad i varje steg (<math><mn>360</mn><mo>&sdot;</mo><mn>1</mn><mo>&deg;</mo><mo>=</mo><mn>360</mn><mo>&deg;</mo></math>), kommer sköldpaddan att rita en jättefin cirkel! Skriv programmet som gör detta.", "import turtle\n\nt = turtle.Turtle()\nt.speed(0) # Gör sköldpaddan supersnabb så du slipper vänta!\n\n# Skapa en for-loop som körs exakt 360 gånger\nfor i in range(   ):\n    # Gå framåt 2 steg och sväng 1 grad åt vänster\n\nturtle.done()")
    upsert_task(db, lesson12.id, 1, 2, "Vi kan göra grafiken finare med färger. Med <code>t.fillcolor('blue')</code> väljer du fyllningsfärg. Innan du börjar rita formen skriver du <code>t.begin_fill()</code>, och när formen är stängd skriver du <code>t.end_fill()</code>.<br><br>Skriv ett program som ritar en valfri stängd geometrisk form (t.ex. en kvadrat eller hexagon) som fylls med en fin färg.", "import turtle\n\nt = turtle.Turtle()\n\nt.fillcolor('cyan')  # Välj din favoritfärg på engelska\nt.begin_fill()       # Starta fyllningen\n\n# Skriv koden som ritar en stängd geometrisk form här\n\nt.end_fill()\n# Avsluta fyllningen och färglägg formen\nturtle.done()")
    upsert_task(db, lesson12.id, 2, 2, "Du ska rita tre kvadrater inuti varandra som delar samma starthörn (nedre vänstra). Den första kvadraten ska ha sidolängden 40, den andra 80 och den tredje 120. Använd en for-loop med en <code>range()</code>-funktion som har ett steg (t.ex. <code>range(40, 121, 40)</code>) för att styra kvadratens storlek dynamiskt!<br><br>Utmaning! Försök fylla kvadraterna med olika färg. <br>Tips: Lägg tre färger i en lista.<img src='/illustrations/turtle-fill-square.png' alt='Fyllda kvadrater med Turtle' class='task-image'>", "import turtle\n\nt = turtle.Turtle()\n\n# Loopen ger variabeln 'storlek' värdena 40, 80 och 120\nfor storlek in range(40, 121, 40):\n    # Inuti den här loopen behöver du en till loop som ritar en kvadrat\n    # Använd variabeln 'storlek' för t.forward()\n\nturtle.done()")
    upsert_task(db, lesson12.id, 3, 2, "Att rita en klassisk femuddig stjärna kräver lite vinkelmatematik. För att linjerna ska korsa varandra rätt och sluta sig till en stjärna måste sköldpaddan göra en skarp sväng på exakt 144 grader i varje spets. Skriv ett program som ritar en stjärna med hjälp av en loop som körs 5 gånger.<br><br>Testa sedan att rita andra stjärnor med udda antal uddar. Kan du räkna ut vad det ska vara för vinkel?", "import turtle\n\nt = turtle.Turtle()\n\n# Skapa en loop som körs 5 gånger\n# Gå framåt (t.ex. 150) och sväng 144 grader åt höger\n\nturtle.done()")
    upsert_task(db, lesson12.id, 4, 2, "Vi kan skapa häftiga mönster genom att låta sköldpaddan gå lite längre för varje varv i loopen. Skapa en loop där loopvariabeln <code>i</code> ökar för varje varv. Låt sköldpaddan gå framåt <code>i</code> steg och sedan svänga exakt 90 grader. Det kommer att skapa en växande spiral!", "import turtle\n\nt = turtle.Turtle()\nt.speed(0)  # Gör så att sköldpaddan ritar så snabbt som möjligt\n\n# En loop där i startar på 10 och ökar med 4 i varje steg upp till 200\nfor i in range(   ):\n    # Gå framåt i steg\n    # Sväng 90 grader åt vänster\n\nturtle.done()")
    upsert_task(db, lesson12.id, 5, 2, "Nu ska vi kombinera nästlade loopar med Turtle för att skapa <q>algoritmisk konst</q>. Idén är enkel: Vi ritar en kvadrat, svänger sköldpaddan lite grann (t.ex. 10 grader), och ritar sedan en ny kvadrat.<br><br>Om vi upprepar detta 36 gånger (<math><mn>36</mn><mo>&sdot;</mo><mn>10</mn><mo>&deg;</mo><mo>=</mo><mn>360</mn><mo>&deg;</mo></math>) kommer vi att ha ritat ett helt varv av överlappande kvadrater, vilket bildar ett komplext och vackert mönster (en geometrisk blomma).", "import turtle\n\nt = turtle.Turtle()\nt.speed(0)  # Maxhastighet\n\n# Den yttre loopen snurrar mönstret ett helt varv (36 * 10 grader = 360)\nfor i in range(   ):\n    # 1. Skriv den inre loopen som ritar EN kvadrat (storlek t.ex. 100)\n\n    # 2. Efter att kvadraten är ritad, sväng 10 grader innan nästa kvadrat påbörjas\n\nturtle.done()")

    db.commit()


@app.post("/api/users", response_model=str)
def create_user(db: Session = Depends(get_db)):
    new_user = database.User()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.id

@app.get("/api/users/{user_id}", response_model=bool)
def check_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == user_id).first()
    return user is not None

@app.get("/api/lessons", response_model=List[LessonSchema])
def get_lessons(db: Session = Depends(get_db)):
    return db.query(database.Lesson).order_by(database.Lesson.lesson_number).all()

@app.get("/api/saved_code/{user_id}")
def get_saved_code(user_id: str, db: Session = Depends(get_db)):
    codes = db.query(database.SavedCode).filter(database.SavedCode.user_id == user_id).all()
    return [{"task_id": c.task_id, "code": c.code} for c in codes]

@app.post("/api/saved_code")
def save_code(req: SaveCodeRequest, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    saved = db.query(database.SavedCode).filter(
        database.SavedCode.user_id == req.user_id,
        database.SavedCode.task_id == req.task_id
    ).first()
    
    if saved:
        saved.code = req.code
    else:
        saved = database.SavedCode(user_id=req.user_id, task_id=req.task_id, code=req.code)
        db.add(saved)
        
    db.commit()
    return {"status": "ok"}


@app.get("/api/activities", response_model=List[ActivitySchema])
def get_activities(db: Session = Depends(get_db)):
    return db.query(database.Activity).order_by(database.Activity.id).all()


@app.get("/api/activities/state/{user_id}/{activity_id}")
def get_activity_state(user_id: str, activity_id: int, db: Session = Depends(get_db)):
    saved_code = db.query(database.ActivitySavedCode).filter_by(user_id=user_id, activity_id=activity_id).first()
    answers = db.query(database.ActivityAnswer).filter_by(user_id=user_id).all()
    ans_dict = {str(a.question_id): a.answer for a in answers}
    return {
        "code": saved_code.code if saved_code else "",
        "answers": ans_dict
    }


@app.post("/api/activities/state")
def save_activity_state(req: SaveActivityAnswerRequest, db: Session = Depends(get_db)):
    user = db.query(database.User).filter(database.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    saved_code = db.query(database.ActivitySavedCode).filter_by(user_id=req.user_id, activity_id=req.activity_id).first()
    if saved_code:
        saved_code.code = req.code
    else:
        db.add(database.ActivitySavedCode(user_id=req.user_id, activity_id=req.activity_id, code=req.code))
        
    for qid, ans in req.answers.items():
        ans_row = db.query(database.ActivityAnswer).filter_by(user_id=req.user_id, question_id=int(qid)).first()
        if ans_row:
            ans_row.answer = ans
        else:
            db.add(database.ActivityAnswer(user_id=req.user_id, question_id=int(qid), answer=ans))
            
    db.commit()
    return {"status": "ok"}


# Mount static files (create dir if not exists)
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_2_germ, menu_2, menu_2_kyrg, menu_2_eng
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from stud_reg import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()



router_germ = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  
if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")

DB_PATH = "bot_db.sqlite3"

init_db()



def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class FSMAdminAddGerm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    latitude = State()
    longitude = State()

class FSMAdminDelGerm(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

keyboard_germ = ReplyKeyboardMarkup(
        keyboard=[        
            [KeyboardButton(text="🔍 Berufe auswählen")],
            [KeyboardButton(text="➕ Benutzer hinzufügen")],
            [KeyboardButton(text="📋 Benutzerliste")],
            [KeyboardButton(text="❌ Benutzer entfernen")]
    ],
    resize_keyboard = True

    )
keyboard_2_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin panel")],
            [KeyboardButton(text="➕ Registrieren")]
        ],
        resize_keyboard=True
    )


@router_germ.message(Command("start_germ"))
async def cmd_start_germ(message: types.Message):

    await message.answer(
            f"""👋 Hello, {message.from_user.first_name}!Willkommen beim Telegram-Bot, der passende OSHsu-Berufe für Sie ermittelt. Sie müssen sich registrieren, bevor Sie diesen Bot nutzen können. Sofern Sie sich bereits registriert haben, drücken Sie /info.

Falls Sie Fragen haben, schreiben Sie an den Bot-Ersteller: @vulpes_07.

Wenn Sie die Sprache ändern möchten, drücken Sie /start

Weitere Informationen zu Berufen und Studiengebühren: https://www.oshsu.kg/ru/page/56

Wählen Sie die Funktion:""",
            reply_markup=keyboard_2_germ
        )

@router_germ.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Willkommen, Administrator {message.from_user.first_name}!\n"
            "🛠 Alle administrativen Funktionen stehen zur Verfügung:",
            reply_markup=keyboard_germ
        )
    else:
        await message.answer(
            "⛔ Sie haben keinen Zugriff auf diesen Befehl",
            reply_markup=keyboard_2_germ
        )

@router_germ.message(F.text == "🛠 Admin panel")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sie haben keine Berechtigung für diese Funktion")
        return
    else:
        await message.answer(
            f"👋 Willkommen zurück, Administrator {message.from_user.first_name}!\n"
            "🛠 Alle administrativen Funktionen sind bereit:",
            reply_markup=keyboard_germ)




@router_germ.message(F.text == "➕ Benutzer hinzufügen")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="de") 
    await start_add_user(message, state)


    
@router_germ.message(F.text == "➕ Registrieren")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="de") 
    await start_add_user(message, state)

@router_germ.message(F.text == "📋 Benutzerliste")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_germ.message(F.text == "❌ Benutzer entfernen")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_germ.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Geben Sie Ihren Namen ein:")
    await state.set_state(FSMAdminAddGerm.name)


@router_germ.message(FSMAdminAddGerm.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Geben Sie Ihr aktuelles Alter ein:")
    await state.set_state(FSMAdminAddGerm.age)

@router_germ.message(FSMAdminAddGerm.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Geben Sie Ihr aktuelles Alter ein.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddGerm.gender) 
    await message.answer("Was ist Ihr Geschlecht:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Mann", callback_data="gender_male")],
        [InlineKeyboardButton(text="Frau", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddGerm.gender)

@router_germ.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Mann" if callback_query.data == "gender_male" else "Frau"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Geben Sie Ihre Telefonnummer ein:")
    await state.set_state(FSMAdminAddGerm.ph_num)

@router_germ.message(FSMAdminAddGerm.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Geben Sie Ihre Telefonnummer ein.")
        return
    await state.update_data(ph_num=int(message.text))




    LOCATION_PROMPTS = {
    "ru": "Отправьте вашу геолокацию, включите локацию на устройстве для определения вашей геопозиции на данный момент ",
    "kg": "Геолокацияңызды жөнөтүңүз, учурдагы геолокацияңызды аныктоо үчүн локация жаңдырыңыз",
    "en": "Send your geolocation, enable location on your device to determine your current geolocation",
    "de": "Senden Sie Ihre Geolokalisierung, aktivieren Sie die Ortung auf Ihrem Gerät, um Ihre aktuelle Geolokalisierung zu bestimmen"
    }

    
    lang = (await state.get_data()).get("lang", "de")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
    reply_markup=menu if lang == "ru" 
    else menu_eng if lang == "en" 
    else menu_germ if lang == "de" 
    else menu_kyrg )
    await state.set_state(FSMAdminAddGerm.latitude)




@router_germ.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"ERROR: {field} - Kein vorhandenes Feld. Erneut registrieren.")
            await state.clear()  
            return

    
    add_user(
        name=user_data["name"],
        age=user_data["age"],
        gender=user_data["gender"],
        ph_num=user_data["ph_num"],
        latitude=message.location.latitude,
        longitude=message.location.longitude,
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )
    SUCCESS_MSGS = {
    "ru": "Ваши данные успешно добавлены! Спасибо за регистрацию, можете воспользоваться функциями бота",
    "en": "The data has been saved successfully! Thank you for the registration, now you can use bot functions",
    "de": "Die Daten wurden erfolgreich gespeichert! Vielen Dank für die Registrierung, jetzt können Sie die Bot-Funktionen nutzen",
    "kg": "Дайындарыңыз ийгиликтүү кошулду! Каттоодон өткөнүңүз үчүн рахмат, боттун мүмкүнчүлүктөрүн колдоно аласыз"
    }
    lang = (await state.get_data()).get("lang", "de")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()  




@router_germ.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "de")
    COMM_LIST_PROMPTS = {
    "ru": "📋Список доступных команд: ",
    "kg": "📋Жеткиликтүү буйруктардын тизмеси: ",
    "en": "📋List of the available cammands: ",
    "de": "📋Liste der verfügbaren Befehle: "
    }
    await message.answer(f"{message.from_user.full_name}, {COMM_LIST_PROMPTS[lang]}",  
    reply_markup=response_menu if lang == "ru" 
    else response_menu_eng if lang == "en" 
    else response_menu_germ if lang == "de" 
    else response_menu_kyrg )




@router_germ.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Sie können diese Funktionen nicht nutzen.")
        return
    users = list_users()
    if not users:
        await message.answer("Es ist kein Benutzer in der Datenbank vorhanden.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username in users:
        location_str = get_address_from_coords(latitude, longitude)
        response_lines.append(f"""
{id}. {name} 
1. Alter: {age}
2. Geshlecht: {gender}
3. Telefonnummer: {ph_num}  
4. username: @{username if username else '-'}
5. Vom Benutzer im Telegramm verwendeter Vor- und Nachname: {first_name} {last_name}
6. ID des Benutzers: {user_id}
7. Standort: {location_str}
8. Standort: latitude: {latitude}, longitude: {longitude}
""") 
    await message.answer(f"📋Liste der Benutzer:\n{''.join(response_lines)}")



@router_germ.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("Es gibt keinen zu entfernenden Benutzer in der Datenbank.")
        return

    kb_germ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Wählen Sie den zu entfernenden Benutzer aus:", reply_markup=kb_germ)


@router_germ.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "de")  


    del_resp = (f"✅ Пользователь {user_id} удалён." if lang == "ru" 
                else f"✅ The user: {user_id} was removed." if lang == "en" 
                else f"✅ Der Benutzer: {user_id} wurde entfernt." if lang == "de"  
                else f"✅ Колдонуучу {user_id} жок кылынды.")

    await callback_query.message.edit_text(del_resp)
    await state.clear() 





from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import os,httpx,sys
from collections import Counter
from stud_reg import is_admin
keyboard_3_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Registrieren")]
        ],
        resize_keyboard=True)



MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
async def ask_mistral(prompt: str) -> str:
    if not MISTRAL_API_KEY:
        return "❌ Ключ MISTRAL_API_KEY не найден!"

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-medium",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=10000.0  
            )
            print("Status:", response.status_code)
            print("Response text:", response.text)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as http_err:
        return f"❌ HTTP ошибка: {http_err.response.status_code}\n{http_err.response.text}"
    except httpx.ReadTimeout:
        return "❌ Ошибка: сервер не ответил вовремя (таймаут)."
    except Exception as e:
        return f"❌ Ошибка запроса: {repr(e)}"

    

    try:
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            print("Status:", response.status_code)
            print("Response text:", response.text)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as http_err:
        return f"❌ HTTP ошибка: {http_err.response.status_code}\n{http_err.response.text}"
    except Exception as e:
        return f"❌ Ошибка запроса: {repr(e)}"


specialties_germ = {
    "INSTITUT FÜR PHILOLOGIE UND INTERKULTURELLE KOMMUNIKATION": [
        "Kirgisische Sprache und Literatur",
        "Staatssprache in Bildungseinrichtungen mit nicht-kirgisischer Unterrichtssprache",
        "Russische Sprache und Literatur",
        "Englische Sprache",
        "Deutsche Sprache",
        "Französische Sprache",
        "Koreanische Sprache",
        "Linguistik: Übersetzung und Übersetzungswissenschaft",
        "Linguistik: Theorie und Methodik des Fremdsprachen- und Kulturunterrichts"
    ],
    "INSTITUT FÜR PÄDAGOGIK, KUNST UND JOURNALISMUS": [
        "Grundschulbildung",
        "Vorschulerziehung und Sprachtherapie",
        "Psychologie",
        "Kunsterziehung",
        "Musikalische Kunst",
        "Bildende Kunst",
        "Popmusik",
        "Design: Modedesign, Innenarchitektur",
        "Kostüm- und Textilkunst",
        "Schauspielkunst",
        "Regie (Kino, Fernsehen)",
        "Kinematografie (Kino, Fernsehen)",
        "Journalismus",
        "Werbung und Öffentlichkeitsarbeit"
    ],
    "HISTORISCHES UND RECHTSWISSENSCHAFTLICHES INSTITUT": [
        "Sozial- und Wirtschaftserziehung: Geschichte",
        "Bibliothekswissenschaft und Dokumentation",
        "Rechtswissenschaft",
        "Zollwesen",
        "Forensische Wissenschaft"
    ],
    "INSTITUT FÜR NATURWISSENSCHAFTEN, SPORT, TOURISMUS UND AGRARTECHNOLOGIEN": [
        "Naturwissenschaftliche Bildung: Biologie",
        "Naturwissenschaftliche Bildung: Chemie",
        "Naturwissenschaftliche Bildung: Geografie",
        "Biologie (Biologie; Biologie und Laborarbeit)",
        "Chemie (Profil: Chemisch-ökologisch, forensisch)",
        "Geografie",
        "Tourismus",
        "Agronomie (Profil: Pflanzenschutz und Quarantäne)",
        "Veterinärmedizin",
        "Angewandte Geodäsie",
        "Körperkultur und Sport"
    ],
    "INSTITUT FÜR MATHEMATIK, PHYSIK, TECHNIK UND INFORMATIONSTECHNOLOGIEN": [
        "Physikalisch-mathematische Bildung: Mathematik und Informatik",
        "Physikalisch-mathematische Bildung: Physik",
        "Angewandte Mathematik und Informatik",
        "Big-Data-Analyse",
        "Angewandte Informatik in der Wirtschaft",
        "Angewandte Informatik in der Architektur",
        "Automatisiertes Geschäftsprozess- und Finanzmanagement",
        "Software von Rechen- und Automatisierungssystemen",
        "Automatisierte Informationsverarbeitung und Steuerungssysteme",
        "Informationssysteme und -technologien in der Wirtschaft",
        "Informationssysteme und -technologien im Bildungswesen",
        "Informationssicherheit",
        "Informatik im Gesundheitswesen und biomedizinische Technik",
        "Mathematische Unterstützung und Verwaltung von Informationssystemen",
        "Webtechnologien und mobile Systemsoftware",
        "Softwareentwicklung für E-Fahrzeuge und Robotiksysteme",
        "Mathematik und Systemanalyse",
        "Computerlinguistik",
        "Design: Grafikdesign",
        "Stromversorgung",
        "Agrartechnik",
        "Architektur",
        "Technische Physik: Medizinische Physik",
        "Technische Physik: Physikalische Methoden der forensischen Untersuchung",
        "Mechatronik und Robotik"
    ],
    "INSTITUT FÜR WIRTSCHAFT, BUSINESS UND MANAGEMENT": [
        "Wirtschaft: Finanzen und Kreditwesen",
        "Wirtschaft: Buchhaltung, Analyse und Prüfung",
        "Wirtschaft: Unternehmensführung",
        "Wirtschaft: Steuern und Besteuerung",
        "Wirtschaft: IT-Buchhaltung",
        "Wirtschaft: Digitale Wirtschaft und mathematische Methoden",
        "Wirtschaft: Wirtschaftsprüfung und Finanzkontrolle",
        "Wirtschaft: Finanzanalytiker im Businessbereich",
        "Wirtschaft: Finanzsicherheit und Finanzkontrolle",
        "Marketing",
        "Wirtschaftsinformatik",
        "Unternehmensführung",
        "Öffentliche und kommunale Verwaltung",
        "Soziale Arbeit"
    ],
    "INSTITUT FÜR OSTWISSENSCHAFTEN": [
        "Orientalistik: Östliche Sprachen und Diplomatie",
        "Orientalistik: Geschichte des Ostens mit Sprachunterricht",
        "Philologie: Östliche Sprachen",
        "Linguistik: Übersetzung und Übersetzungswissenschaft: Östliche Sprachen",
        "Konfliktforschung: Allgemeine Konfliktforschung"
    ],
    "HOCHSCHULE FÜR INTERNATIONALE BILDUNGSPROGRAMME": [
        "Regionalstudien: Ostasien",
        "Grundschulbildung mit Englisch",
        "Mathematik und Informatik",
        "Computermodellierung im Ingenieurwesen und technischen Design",
        "Digitale Diplomatie in den internationalen Beziehungen",
        "Internettechnologien und Management",
        "Wirtschaft: Weltwirtschaft",
        "Europastudien",
        "Unternehmensführung: Internationales Business",
        "Englische Sprache mit Zusatzprofil: Übersetzung und Übersetzungswissenschaft",
        "Englische Sprache mit Zusatzprofil: Computerlinguistik",
        "Internationale Beziehungen",
        "Globale Integration und internationale Organisationen",
        "Politikwissenschaft"
    ],
    "KIRGISISCH-CHINESISCHE FAKULTÄT": [
        "Chinastudien",
        "Linguistik: Übersetzung und Übersetzungswissenschaft",
        "Informatik und Technologien",
        "Elektronische Informationstechnik",
        "Philologie: Methodik des Unterrichts philologischer Fächer (Englisch, Chinesisch)"
    ],
    "MEDIZINISCHE FAKULTÄT": [
        "Allgemeinmedizin",
        "Pädiatrie",
        "Präventionsmedizin",
        "Zahnmedizin",
        "Pharmazie",
        "Pflege",
        "Labordiagnostik"
    ],
    "THEOLOGISCHE FAKULTÄT": [
        "Theologie"
    ],
    "ARASHAN-HUMANITÄR-INSTITUT": [
        "Theologie"
    ]
}


question_fields_germ = []
for faculty_germ, questions_germ in [
    ("Institut für Mathematik, Physik, Technik und Informationstechnologien", [
        "🧠 Löst du gerne logische Rätsel und Denksportaufgaben?",
        "💻 Interessierst du dich für Programmierung oder digitale Technologien?",
        "🔬 Faszinieren dich exakte Wissenschaften wie Mathematik und Physik?",
        "🤖 Bist du neugierig auf Technologie, Elektronik oder Roboter?",
        "🏛️ Interessierst du dich für Architektur, Innenarchitektur oder Bauwesen?",
        "📱 Möchtest du mobile Apps, Webseiten oder Spiele entwickeln?",
        "🧩 Magst du es, Algorithmen, Logik und die Struktur von Programmen zu verstehen?",
        "🔧 Interessierst du dich dafür, wie Maschinen, Geräte oder Roboter funktionieren?",
        "🎮 Möchtest du deine eigenen Spiele, Simulationen oder VR-Welten erstellen?",
        "🌐 Fragst du dich, wie Netzwerke, Informationssicherheit und Cybersicherheit funktionieren?"
    ]),
    ("Institut für Wirtschaft, Business und Management", [
        "📊 Analysierst du gerne Daten und arbeitest mit Zahlen?",
        "💰 Möchtest du eine Karriere in Wirtschaft, Finanzen oder Business machen?",
        "📈 Interessierst du dich für Geschäftsstrategien, Projektmanagement oder Start-ups?",
        "📦 Möchtest du Logistik, Lieferprozesse oder Lagerautomatisierung optimieren?"
    ]),
    ("Medizinische Fakultät", [
        "🩺 Interessierst du dich für Medizin, Gesundheit oder Biotechnologie?",
        "🏥 Bist du bereit, Anatomie, Physiologie und medizinische Grundlagen zu lernen?",
        "🧬 Interessierst du dich für Biologie, Genetik oder Biomedizin?"
    ]),
    ("Institut für Pädagogik, Kunst und Journalistik", [
        "🤝 Möchtest du Menschen helfen, Lebens- oder psychologische Probleme zu lösen?",
        "🎨 Fühlst du dich zur Kreativität, Kunst oder Design hingezogen?",
        "👩‍🏫 Magst du es, Wissen zu teilen und andere zu unterrichten?",
        "🎥 Interessierst du dich für Medien, Film, Journalismus oder öffentliches Sprechen?",
        "🎤 Fühlst du dich wohl dabei, vor Publikum zu sprechen und Präsentationen zu halten?",
        "🧠 Interessierst du dich für menschliches Denken und wie man anderen bei Herausforderungen helfen kann?",
        "👩‍🏫 Möchtest du Lehrer oder Mentor werden und anderen etwas beibringen?",
        "🎨 Möchtest du Interfaces, visuelle Stile oder Grafiken gestalten?"
    ]),
    ("Hochschule für Internationale Bildungsprogramme", [
        "🌍 Möchtest du an internationalen Projekten teilnehmen oder im Ausland arbeiten?",
        "🌏 Möchtest du in der Diplomatie arbeiten, an internationalen Verhandlungen teilnehmen oder Geopolitik studieren?"
    ]),
    ("Institut für Philologie und interkulturelle Kommunikation", [
        "🈴 Lernst du gerne Fremdsprachen und Kulturen anderer Länder?",
        "📚 Magst du es, klassische Literatur zu studieren und zu forschen?",
        "📝 Interessierst du dich für das Schreiben von Essays, Artikeln, Geschichten oder Blogs (letzte Frage – geben Sie dem Bot etwas Zeit (ein paar Sekunden), um Ihre Antworten zu verarbeiten)?"
    ])
]:
    for q_germ in questions_germ:
        question_fields_germ.append((q_germ, faculty_germ))

class CareerTestGerm(StatesGroup):
    q_index = State()
    answers = State()

def yes_no_kb_germ(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ja", callback_data=f"yes_germ_{index}"),
         InlineKeyboardButton(text="Nein", callback_data=f"no_germ_{index}")]
    ])

from stud_reg import is_admin
from database import is_registered

@router_germ.message(F.text == "🔍 Berufe auswählen")
async def start_test_germ(message: types.Message, state: FSMContext):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Für die Nutzung der Bot-Funktionen ist eine Registrierung erforderlich.", reply_markup=keyboard_3_germ)
        return

    await message.answer(question_fields_germ[0][0], reply_markup=yes_no_kb_germ(0))
    await state.update_data(q_index=0, answers=[], lang="de")
    await state.set_state(CareerTestGerm.q_index)

@router_germ.callback_query(lambda c: c.data.startswith(("yes_germ_", "no_germ_")))
async def handle_answer_germ(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("q_index", 0)
    answers = data.get("answers", [])

    current_index = int(callback.data.split("_")[1])
    if current_index != index:
        await callback.answer()
        return

    if callback.data.startswith("yes_germ"):
        answers.append(question_fields_germ[index][1])

    index += 1

    if index < len(question_fields_germ):
        await state.update_data(q_index=index, answers=answers)
        question_text = question_fields_germ[index][0]
        await callback.message.edit_text(question_text, reply_markup=yes_no_kb_germ(index))
    else:
        await state.clear()
        interests = Counter(answers)
        




def generate_prompt_germ(interests):
    return (
        "Sie sind ein professioneller Karriereberater. Basierend auf den Antworten des Benutzers empfehlen Sie die am besten geeigneten Studiengänge. "
        "Ausgabeformat:\n\n"
        "1. Listen Sie zuerst 3-5 passende Institute/Fakultäten in Reihenfolge der Relevanz auf\n"
        "2. Für jedes Institut geben Sie 2-3 am besten passende Studiengänge an\n"
        "3. Fügen Sie eine kurze Erklärung hinzu (1 Satz)\n"
        "4. Verwenden Sie nur Studiengänge aus der bereitgestellten Liste\n\n"
        "Interessen des Benutzers:\n"
        f"{', '.join(interests)}\n\n"
        "Verfügbare Institute und Studiengänge:\n"
        "\n".join([f"🎓 *{k}*:\n   - " + "\n   - ".join(v) for k, v in specialties_germ.items()]) +
        "\n\n"
        "Formatieren Sie Ihre Antwort wie folgt:\n"
        "🏛 *Name des Instituts*\n"
        "   ✨ Studiengang 1 (kurze Begründung)\n"
        "   ✨ Studiengang 2 (kurze Begründung)\n"
        "   ...\n\n"
        "Seien Sie präzise und verwenden Sie nur die bereitgestellten Daten. Answer using only German language"
    )

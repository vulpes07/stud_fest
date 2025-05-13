import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_2_eng, menu_2, menu_2_germ, menu_2_kyrg
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from stud_reg import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()




router_eng = Router()

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

class FSMAdminAddEng(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    latitude = State()
    longitude = State()

class FSMAdminDelEng(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID



keyboard_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Choose professions")],
            [KeyboardButton(text="➕ Add users")],
            [KeyboardButton(text="📋 List of the users")],
            [KeyboardButton(text="❌ Remove the user")]
        ],
        resize_keyboard=True
    )
keyboard_2_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin Panel")],
            [KeyboardButton(text="➕ Register")]
        ],
        resize_keyboard=True
    )
    




@router_eng.message(Command("start_eng"))
async def cmd_start_eng(message: types.Message):
    keyboard_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Choose professions")],
            [KeyboardButton(text="➕ Add users")],
            [KeyboardButton(text="📋 List of the users")],
            [KeyboardButton(text="❌ Remove the user")]
        ],
        resize_keyboard=True
    )
    keyboard_2_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin Panel")],
            [KeyboardButton(text="➕ Register")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
            f"""👋 Hello, {message.from_user.first_name}! Welcome to the telegram bot that can determine some OSHsu professions that suit you. You have to register before you use this bot. Provided by you have already registered, press /info.

In case you have some questions, write to the bot creator: @vulpes_07.

If you want to change the language, press /start

For additional information abot professions and tuition fees: https://www.oshsu.kg/ru/page/56

Choose the function:""",
            reply_markup=keyboard_2_eng
        )

@router_eng.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Welcome, Administrator {message.from_user.first_name}!\n"
            "🛠 All administrative functions are available:",
            reply_markup=keyboard_eng
        )
    else:
        await message.answer(
            "⛔ You don't have access to this command",
            reply_markup=keyboard_2_eng
        )

@router_eng.message(F.text == "🛠 Admin Panel")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ You don't have permission to access this feature")
        return
    else:
        await message.answer(
            f"👋 Welcome back, Administrator {message.from_user.first_name}!\n"
            "🛠 All administrative functions are ready:",
            reply_markup=keyboard_eng)



@router_eng.message(F.text == "➕ Add user")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="en") 
    await start_add_user(message, state)


@router_eng.message(F.text == "➕ Register")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="en") 
    await start_add_user(message, state)

@router_eng.message(F.text == "📋 List of the users")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_eng.message(F.text == "❌ Remove the user")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_eng.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Enter your name: ")
    await state.set_state(FSMAdminAddEng.name)


@router_eng.message(FSMAdminAddEng.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Enter your current age:")
    await state.set_state(FSMAdminAddEng.age)

@router_eng.message(FSMAdminAddEng.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Enter your current age.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddEng.gender) 
    await message.answer("What's your gender:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="gender_male")],
        [InlineKeyboardButton(text="Female", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddEng.gender)

@router_eng.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Male" if callback_query.data == "gender_male" else "Female"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Enter your phone number:")
    await state.set_state(FSMAdminAddEng.ph_num)


@router_eng.message(FSMAdminAddEng.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Enter you phone number.")
        return
    await state.update_data(ph_num=int(message.text))




    LOCATION_PROMPTS = {
    "ru": "Отправьте вашу геолокацию, включите локацию на устройстве для определения вашей геопозиции на данный момент ",
    "kg": "Геолокацияңызды жөнөтүңүз, учурдагы геолокацияңызды аныктоо үчүн локация жаңдырыңыз",
    "en": "Send your geolocation, enable location on your device to determine your current geolocation",
    "de": "Senden Sie Ihre Geolokalisierung, aktivieren Sie die Ortung auf Ihrem Gerät, um Ihre aktuelle Geolokalisierung zu bestimmen"
    }

    
    lang = (await state.get_data()).get("lang", "en")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
    reply_markup=menu if lang == "ru" 
    else menu_eng if lang == "en" 
    else menu_germ if lang == "de" 
    else menu_kyrg )
    await state.set_state(FSMAdminAddEng.latitude)






@router_eng.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"ERROR: {field} - no existing field. Register again.")
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
    lang = (await state.get_data()).get("lang", "en")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()  





@router_eng.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "en")
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






@router_eng.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("You are not able to use this functions.")
        return
    users = list_users()
    if not users:
        await message.answer("The is no user in data base.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username in users:
        location_str = get_address_from_coords(latitude, longitude)
        response_lines.append(f"""
{id}. {name} 
1. Age: {age}
2. Sex: {gender}
3. Phone number: {ph_num}  
4. username: @{username if username else '-'}
5. First name and last name used by the user in telegram: {first_name} {last_name}
6. ID of the user: {user_id}
7. Location: {location_str}
8. Location: latitude: {latitude}, longitude: {longitude}
""") 
    await message.answer(f"📋List of the users:\n{''.join(response_lines)}")



@router_eng.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("There is no user in data base to remove.")
        return

    kb_eng = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Choose the user to remove:", reply_markup=kb_eng)


@router_eng.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "en")  


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
keyboard_3_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Register")]
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


specialties_eng = {
    "INSTITUTE OF PHILOLOGY AND INTERCULTURAL COMMUNICATION": [
        "Kyrgyz Language and Literature",
        "State Language in Educational Institutions with Non-Kyrgyz Language of Instruction",
        "Russian Language and Literature",
        "English Language",
        "German Language",
        "French Language",
        "Korean Language",
        "Linguistics: Translation and Translation Studies",
        "Linguistics: Theory and Methods of Teaching Foreign Languages and Cultures"
    ],
    "INSTITUTE OF PEDAGOGY, ART AND JOURNALISM": [
        "Primary Education",
        "Preschool Education and Speech Therapy",
        "Psychology",
        "Art Education",
        "Musical Art",
        "Fine Arts",
        "Pop Music Art",
        "Design: Costume Design, Interior Design",
        "Art of Costume and Textiles",
        "Acting",
        "Directing (Film, TV)",
        "Cinematography (Film, TV)",
        "Journalism",
        "Advertising and Public Relations"
    ],
    "HISTORICAL AND LEGAL INSTITUTE": [
        "Social and Economic Education: History",
        "Library and Documentation Science",
        "Jurisprudence",
        "Customs Affairs",
        "Forensic Expertise"
    ],
    "INSTITUTE OF NATURAL SCIENCES, PHYSICAL EDUCATION, TOURISM AND AGRICULTURAL TECHNOLOGIES": [
        "Natural Science Education: Biology",
        "Natural Science Education: Chemistry",
        "Natural Science Education: Geography",
        "Biology (Biology; Biology and Laboratory Work)",
        "Chemistry (Profile: Chemical-Ecological, Forensic Expertise)",
        "Geography",
        "Tourism",
        "Agronomy (Profile: Plant Quarantine Protection)",
        "Veterinary Medicine",
        "Applied Geodesy",
        "Physical Culture and Sports"
    ],
    "INSTITUTE OF MATHEMATICS, PHYSICS, ENGINEERING AND INFORMATION TECHNOLOGIES": [
        "Physical and Mathematical Education: Mathematics and Computer Science",
        "Physical and Mathematical Education: Physics",
        "Applied Mathematics and Informatics",
        "Big Data Analytics",
        "Applied Informatics in Economics",
        "Applied Informatics in Architecture",
        "Automated Management of Business Processes and Finance",
        "Software for Computing Equipment and Automated Systems",
        "Automated Information Processing and Management Systems",
        "Information Systems and Technologies in Economics",
        "Information Systems and Technologies in Education",
        "Information Security",
        "Computer Science in Healthcare and Biomedical Engineering",
        "Mathematical Support and Administration of Information Systems",
        "Web Technologies and Mobile Systems Software",
        "Software Development for Electric Vehicles and Robotic Systems",
        "Mathematics and Systems Analysis",
        "Computational Linguistics",
        "Design: Graphic Design",
        "Electric Power Supply",
        "Agroengineering",
        "Architecture",
        "Technical Physics: Medical Physics",
        "Technical Physics: Forensic Methods",
        "Mechatronics and Robotics"
    ],

    "INSTITUTE OF ECONOMICS, BUSINESS AND MANAGEMENT": [
        "Economics: Finance and Credit",
        "Economics: Accounting, Analysis and Audit",
        "Economics: Economics and Enterprise Management",
        "Economics: Taxation",
        "Economics: IT Accounting",
        "Economics: Digital Economy and Mathematical Methods",
        "Economics: Audit and Financial Control",
        "Economics: Financial Analyst in Business",
        "Economics: Financial Security and Financial Control",
        "Marketing",
        "Business Informatics",
        "Business Management",
        "Public and Municipal Administration",
        "Social Work"
    ],

    "INSTITUTE OF ORIENTAL STUDIES": [
        "Oriental Studies: Eastern Languages and Diplomacy",
        "Oriental Studies: History of the East with Teaching of Eastern Languages",
        "Philology: Eastern Languages",
        "Linguistics: Translation and Translation Studies: Eastern Languages",
        "Conflictology: General Conflictology"
    ],

    "HIGHER SCHOOL OF INTERNATIONAL EDUCATIONAL PROGRAMS": [
        "Regional Studies: East Asia",
        "Primary Education. English Language",
        "Mathematics and Computer Science",
        "Computer Modeling in Engineering and Technological Design",
        "Digital Diplomacy in International Relations",
        "Internet Technologies and Management",
        "Economics: World Economy",
        "European Studies",
        "Business Management: International Business",
        "English Language with Additional Specialization: Translation and Translation Studies",
        "English Language with Additional Specialization: Computational Linguistics",
        "International Relations",
        "Global Integration and International Organizations",
        "Political Science"
    ],

    "KYRGYZ-CHINESE FACULTY": [
        "Chinese Studies",
        "Linguistics: Translation and Translation Studies",
        "Computer Science and Technologies",
        "Electronic Information Engineering",
        "Philology: Methods of Teaching Philological Disciplines (English, Chinese)"
    ],
    "MEDICAL FACULTY": [
        "General Medicine",
        "Pediatrics",
        "Preventive Medicine",
        "Dentistry",
        "Pharmacy",
        "Nursing",
        "Laboratory Science",
    ],
    "THEOLOGICAL FACULTY": [
        "Theology"
    ],

    "ARASHAN HUMANITIES INSTITUTE": [
        "Theology"
    ]
}

question_fields_eng = []
for faculty_eng, questions_eng in [
    ("Institute of Mathematics, Physics, Technology, and Information Technologies", [
        "🧠 Do you enjoy solving logic puzzles and riddles?",
        "💻 Are you interested in programming or digital technologies?",
        "🔬 Are you fascinated by exact sciences like mathematics and physics?",
        "🤖 Are you curious about technology, electronics, or robots?",
        "🏛️ Are you interested in architecture, interior design, or construction?",
        "📱 Would you like to create mobile apps, websites, or games?",
        "🧩 Do you enjoy understanding algorithms, logic, and program structures?",
        "🔧 Are you interested in how mechanisms, equipment, or robots work?",
        "🎮 Would you like to create your own games, simulations, or VR worlds?",
        "🌐 Are you wondering how internet networks, information security, and cybersecurity work?"
    ]),
    ("Institute of Economics, Business, and Management", [
        "📊 Do you enjoy analyzing data and working with numbers?",
        "💰 Do you want to build a career in economics, finance, or business?",
        "📈 Are you interested in business strategies, project management, or startups?",
        "📦 Would you like to optimize logistics, delivery processes, or warehouse automation?"
    ]),
    ("Medical Faculty", [
        "🩺 Are you interested in medicine, health, or biotechnology?",
        "🏥 Are you ready to study anatomy, physiology, and the basics of medicine?",
        "🧬 Are you curious about biology, genetics, or biomedicine?"
    ]),
    ("Institute of Pedagogy, Art, and Journalism", [
        "🤝 Do you want to help people solve life or psychological challenges?",
        "🎨 Are you drawn to creativity, art, or design?",
        "👩‍🏫 Do you enjoy sharing knowledge and teaching others?",
        "🎥 Are you interested in media, film, journalism, or public speaking?",
        "🎤 Are you comfortable speaking in front of an audience and giving presentations?",
        "🧠 Are you fascinated by human thinking and how to help people deal with challenges?",
        "👩‍🏫 Do you want to teach and become a mentor or educator?",
        "🎨 Would you like to design interfaces, visual styles, or graphics?"
    ]),
    ("Higher School of International Educational Programs", [
        "🌍 Do you want to participate in international projects or work abroad?",
        "🌏 Do you want to work in diplomacy, take part in international negotiations, or study geopolitics?"
    ]),
    ("Institute of Philology and Intercultural Communication", [
        "🈴 Do you enjoy learning foreign languages and cultures?",
        "📚 Do you like studying classic literature and conducting research?",
        "📝 Are you interested in writing: essays, articles, stories, or blogs (last question - give the bot some time (a couple of seconds) to process your answers)?"
    ])
]:
    for q_eng in questions_eng:
        question_fields_eng.append((q_eng, faculty_eng))

class CareerTestEng(StatesGroup):
    q_index = State()
    answers = State()

def yes_no_kb_eng(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data=f"yes_eng_{index}"),
         InlineKeyboardButton(text="No", callback_data=f"no_eng_{index}")]
    ])

from stud_reg import is_admin
from database import is_registered

@router_eng.message(F.text == "🔍 Choose professions")
async def start_test_eng(message: types.Message, state: FSMContext):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("You have to register for the purpose of using bot functions.", reply_markup=keyboard_3_eng)
        return

    await message.answer(question_fields_eng[0][0], reply_markup=yes_no_kb_eng(0))
    await state.update_data(q_index=0, answers=[], lang="en")
    await state.set_state(CareerTestEng.q_index)

@router_eng.callback_query(lambda c: c.data.startswith(("yes_eng_", "no_eng_")))
async def handle_answer_eng(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("q_index", 0)
    answers = data.get("answers", [])

    current_index = int(callback.data.split("_")[1])
    if current_index != index:
        await callback.answer()
        return

    if callback.data.startswith("yes_eng"):
        answers.append(question_fields_eng[index][1])

    index += 1

    if index < len(question_fields_eng):
        await state.update_data(q_index=index, answers=answers)
        question_text = question_fields_eng[index][0]
        await callback.message.edit_text(question_text, reply_markup=yes_no_kb_eng(index))
    else:
        await state.clear()
        interests = Counter(answers)
        

   
def generate_prompt_eng(interests):
    return (
        "You are a professional career counselor. Based on the user's answers, recommend the most suitable specialties. "
        "Output format:\n\n"
        "1. First list 3-5 most relevant institutes/faculties in order of relevance\n"
        "2. For each institute, suggest 2-3 most suitable specialties\n"
        "3. Provide a brief explanation (1 sentence) for each recommendation\n"
        "4. Use only specialties from the provided list\n\n"
        "User's interests:\n"
        f"{', '.join(interests)}\n\n"
        "Available institutes and specialties:\n"
        "\n".join([f"🎓 *{k}*:\n   - " + "\n   - ".join(v) for k, v in specialties_eng.items()]) +
        "\n\n"
        "Format your response like this:\n"
        "🏛 *Institute name*\n"
        "   ✨ Specialty 1 (brief explanation)\n"
        "   ✨ Specialty 2 (brief explanation)\n"
        "   ...\n\n"
        "Be concise, precise and use only the provided data. Answer using only English language"
    )

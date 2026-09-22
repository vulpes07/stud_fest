import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_2, menu_2_eng, menu_2_germ, menu_2_kyrg
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from stud_reg import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()



router_kyrg = Router()

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

class FSMAdminAddKyrg(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    latitude = State()
    longitude = State()

class FSMAdminDelKyrg(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID



keyboard_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Кесип тандоо")],
            [KeyboardButton(text="➕ Колдонуучу кошуу")],
            [KeyboardButton(text="📋 Колдонуучулардын тизмеси")],
            [KeyboardButton(text="❌ Колдонуучуну жок кылуу")]
        ],
        resize_keyboard=True
    )
keyboard_2_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ панель")],
            [KeyboardButton(text="➕ Катталуу")]
        ],
        resize_keyboard=True
    )


@router_kyrg.message(Command("start_kyrg"))
async def cmd_start_kyrg(message: types.Message):

    await message.answer(
            f"""👋 Салам, {message.from_user.first_name}! Сиз ОшМУда окутулган сизге ылайыктуу кесипти аныктоо үчүн ботко кош келиңиз. Боттун функцияларын колдонуудан мурун, каттоодон өтүңүз. Ал эми сиз буга чейин катталган болсоңуз, /info басыңыз.

Тилди өзгөртүүнү кааласаңыз, /start баскычын басыңыз            

Бардык кошумча суроолор боюнча боттун жаратуучусуна кайрылыңыз: @vulpes_07.

Бул сайтта адистиктер жана кабыл алуулар жөнүндө толук маалымат: https://www.oshsu.kg/ru/page/56

Функцияны тандаңыз:""",
            reply_markup=keyboard_2_kyrg
        )


@router_kyrg.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Саламатсызбы, администратор {message.from_user.first_name}!\n"
            "🛠 Сизге бардык административдик функциялар жеткиликтүү:",
            reply_markup=keyboard_kyrg
        )
    else:
        await message.answer(
            "⛔ Бул буйрукка кирүү укугуңуз жок",
            reply_markup=keyboard_2_kyrg
        )

@router_kyrg.message(F.text == "🛠 Админ панель")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Бул функцияга кирүү укугуңуз жок")
        return
    else:
        await message.answer(
            f"👋 Саламатсызбы, администратор {message.from_user.first_name}!\n"
            "🛠 Сизге бардык административдик функциялар жеткиликтүү:",
            reply_markup=keyboard_kyrg)




@router_kyrg.message(F.text == "➕ Колдонуучу кошуу")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="kg")  
    await start_add_user(message, state)

@router_kyrg.message(F.text == "➕ Катталуу")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="kg")  
    await start_add_user(message, state)

@router_kyrg.message(F.text == "📋 Колдонуучулардын тизмеси")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_kyrg.message(F.text == "❌ Колдонуучуну жок кылуу")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_kyrg.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Атыңызды жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.name)


@router_kyrg.message(FSMAdminAddKyrg.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Жашынызды жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.age)

@router_kyrg.message(FSMAdminAddKyrg.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Жашынызды жазыңыз.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddKyrg.gender) 
    await message.answer("Жынысыңызды тандаңыз:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Эркек", callback_data="gender_male")],
        [InlineKeyboardButton(text="Аял", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddKyrg.gender)

@router_kyrg.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Эркек" if callback_query.data == "gender_male" else "Аял"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Телефон номериңизди жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.ph_num)


@router_kyrg.message(FSMAdminAddKyrg.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Телефон номериңизди жазыңыз.")
        return
    await state.update_data(ph_num=int(message.text))

    


    LOCATION_PROMPTS = {
    "ru": "Отправьте вашу геолокацию, включите локацию на устройстве для определения вашей геопозиции на данный момент ",
    "kg": "Геолокацияңызды жөнөтүңүз, учурдагы геолокацияңызды аныктоо үчүн локация жаңдырыңыз",
    "en": "Send your geolocation, enable location on your device to determine your current geolocation",
    "de": "Senden Sie Ihre Geolokalisierung, aktivieren Sie die Ortung auf Ihrem Gerät, um Ihre aktuelle Geolokalisierung zu bestimmen"
    }

    
    lang = (await state.get_data()).get("lang", "kg")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
    reply_markup=menu if lang == "ru" 
    else menu_eng if lang == "en" 
    else menu_germ if lang == "de" 
    else menu_kyrg )
    await state.set_state(FSMAdminAddKyrg.latitude)




@router_kyrg.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"Ката кетти: {field} талаасы жок. Каттоону кайра баштоого аракет кылыңыз.")
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

    lang = (await state.get_data()).get("lang", "kg")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()  





@router_kyrg.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "kg")
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




@router_kyrg.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Бул командага колдонууга мүмкүнчүлүгүңүз жок.")
        return
    users = list_users()
    if not users:
        await message.answer("Маалыматтар базасында колдонуучулар жок.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username in users:
        location_str = get_address_from_coords(latitude, longitude)
        response_lines.append(f"""
{id}. {name} 
1. Жашы: {age}
2. Жынысы: {gender}
3. Телефондун номери: {ph_num}  
4. username: @{username if username else '-'}
5. Колдонуучу тарабынан көрсөтүлгөн аты жана фамилиясы телеграмда: {first_name} {last_name}
6. Колдонуучунун ID - си: {user_id}
7. Локация: {location_str}
8. Локация: широта: {latitude}, долгота: {longitude}
""") 
    await message.answer(f"📋Колдонуучулардын тизмеси:\n{''.join(response_lines)}")



@router_kyrg.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("Маалымат базасында жок кылуу үчүн колдонуучулар жок.")
        return

    kb_kyrg = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Жок кылуу үчүн колдонуучуну тандаңыз:", reply_markup=kb_kyrg)


@router_kyrg.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "kg") 


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
keyboard_3_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Катталуу")]
        ],
        resize_keyboard=True)



import asyncio  

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def ask_mistral(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "❌ Ключ GEMINI_API_KEY не найден!"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    max_retries = 4
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=60.0)

                if response.status_code == 503:
                    wait = 3 * (attempt + 1)  # 3, 6, 9, 12 секунд
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

        except httpx.HTTPStatusError as http_err:
            return f"❌ HTTP ошибка: {http_err.response.status_code}\n{http_err.response.text}"
        except httpx.ReadTimeout:
            return "❌ Ошибка: сервер не ответил вовремя (таймаут)."
        except Exception as e:
            return f"❌ Ошибка запроса: {repr(e)}"

    return "❌ Сервис Gemini сейчас перегружен. Попробуйте пройти тест ещё раз через минуту."
    

specialties_kyrg = {
    "Филология жана маданиятаралык коммуникация институту":[
    "Кыргыз тили жана адабияты",
    "Билим берүү мекемелеринде кыргыз эмес тилде окутуудагы мамлекеттик тил",
    "Орус тили жана адабияты",
    "Англис тили",
    "Немис тили",
    "Француз тили",
    "Корей тили",
    "Лингвистика: Котормо жана котормо таануу",
    "Лингвистика: Чет тилдерин жана маданияттарды окутуунун теориясы жана методикасы"
    ],


    "Педагогика, искусство жана журналистика институту":[
    "Башталгыч билим",
    "Мектепке чейинки билим жана логопедия",
    "Психология",
    "Көркөм билим",
    "Музыка искусствосу",
    "Сүрөт искусствосу",
    "Эстрадалык музыка искусствосу",
    "Дизайн: кийим дизайны, интерьер дизайны",
    "Кийим жана текстиль искусствосу",
    "Актердук искусство",
    "Режиссура (Кино, ТВ)",
    "Кинооператорлук (Кино, ТВ)",
    "Журналистика",
    "Жарыялоо жана коомдук мамилелер"
    ],


    "Тарыхый-юридикалык институт": [
    "Социалдык-экономикалык билим: Тарых",
    "Китепкана таануу жана документ таануу",
    "Юриспруденция",
    "Кызмат иши",
    "Сот экспертизасы"
    ],



    "Жаратылыш илимдери, дене тарбиясы, туризм жана агрардык технологиялар институту":[
    "Жаратылыш илимдери: Биология",
    "Жаратылыш илимдери: Химия",
    "Жаратылыш илимдери: География",
    "Биология (Биология; Биология жана лабораториялык иш)",
    "Химия (профиль: химия-экологиялык, криминалистикалык экспертиза)",
    "География",
    "Туризм",
    "Агрономия (профиль: карантиндик өсүмдүктөрдү коргоо)",
    "Ветеринария",
    "Колдонмо геодезия",
    "Дене тарбиясы жана спорт"
    ],




    "Математика, физика, техника жана информатикалык технологиялар институту": [
    "Физика-математикалык билим: Математика жана информатика",
    "Физика-математикалык билим: Физика",
    "Колдонмо математика жана информатика",
    "Big Data аналитика",
    "Экономикада колдонмо информатика",
    "Архитектурада колдонмо информатика",
    "Бизнес-процесстерди жана финансыларды автоматташтырылган башкаруу",
    "Эсептөө техникасынын жана автоматташтырылган системдердин программалык камсыздоосу (ПОВТАС)",
    "Маалыматтарды иштетүүнүн жана башкаруунун автоматташтырылган системдери (АСОИУ)",
    "Экономикада маалыматтык системдер жана технологиялар",
    "Билим берүүдө маалыматтык системдер жана технологиялар",
    "Маалыматтык коопсуздук",
    "Ден соолукта информатика жана биомедициналык инженерия",
    "Маалыматтык системдердин математикалык камсыздоосу жана администрирлөөсү",
    "Веб-технологиялар жана мобилдик системдердин программалык камсыздоосу",
    "Электромобилдерди жана робототехникалык системдерди башкаруу үчүн программаларды иштеп чыгуу",
    "Математика жана системдик анализ",
    "Компьютердик лингвистика",
    "Дизайн: графикалык дизайн",
    "Электр менен жабдуу",
    "Агроинженерия",
    "Архитектура",
    "Техникалык физика: Медициналык физика",
    "Техникалык физика: Криминалистикалык экспертизанын физикалык методдору",
    "Мехатроника жана робототехника"
    ],



    "Экономика, бизнес жана менеджмент институту": [
    "Экономика: Финансы жана кредит",
    "Экономика: Бухгалтердик эсеп, анализ жана аудит",
    "Экономика: Ишканадагы экономика жана башкаруу",
    "Экономика: Салык жана салык салуу",
    "Экономика: IT-Бухгалтерия",
    "Экономика: Сандык экономика жана математикалык методдор",
    "Экономика: Аудит жана финансылык көзөмөл",
    "Экономика: Бизнесте финансылык аналитик",
    "Экономика: Финансылык коопсуздук жана финансылык көзөмөл",
    "Маркетинг",
    "Бизнес информатика",
    "Бизнес башкаруу",
    "Мамлекеттик жана муниципалдык башкаруу",
    "Коомдук иш"
    ],



    "Чыгыш таануу институту": [
    "Чыгыш таануу: Чыгыш тилдери жана дипломатия",
    "Чыгыш таануу: Чыгыш тарыхы – чыгыш тилдерин окутуу менен",
    "Филология: Чыгыш тилдери",
    "Лингвистика: Котормо жана котормо таануу: Чыгыш тилдери",
    "Конфликтология: Жалпы конфликтология"
    ],




    "Эл аралык билим берүү программаларынын жогорку мектеби": [
    "Аймак таануу: Чыгыш Азия",
    "Башталгыч билим. Англис тили",
    "Математика жана компьютердик илимдер",
    "Инженердик жана технологиялык долбоорлоодо компьютердик моделирлөө",
    "Эл аралык мамилелерде сандык дипломатия",
    "Интернет технологиялары жана башкаруу",
    "Экономика: Дүйнөлүк экономика",
    "Европа таануу",
    "Бизнес башкаруу: Эл аралык бизнес",
    "Англис тили кошумча профиль менен: Котормо жана котормо таануу",
    "Англис тили кошумча профиль менен: Компьютердик лингвистика",
    "Эл аралык мамилелер",
    "Дүйнөлүк интеграция жана эл аралык уюмдар",
    "Политология"
    ],



    "Кыргыз-Кытай факультети": [
    "Кытай таануу",
    "Лингвистика: Котормо жана котормо таануу",
    "Информатика жана технологиялар",
    "Электрондук маалыматтык инженерия",
    "Филология: Филологиялык дисциплиналарды окутуу методикасы (Англис тили, Кытай тили)"
    ],



    "Медицина факультети": [
    "Дарылоо иши",
    "Педиатрия",
    "Медицина-алдын алуу иши",
    "Стоматология",
    "Фармация",
    "Медсестралык иш",
    "Лабораториялык иш",
    ],



    "Теология факультети": [
    "Теология"],



    "Арашан гуманитардык институту": [
    "Теология"]
}


question_fields_kyrg = []
for faculty_kyrg, questions_kyrg in [
    ("Математика, физика, техника жана информатикалык технологиялар институту", [
        "🧠 Сиз логикалык маселелерди жана табышмактарды чечкенди жактырасызбы?",
        "💻 Сиз программалоого же санариптик технологияга кызыгасызбы?",
        "🔬 Сизди математика жана физика сыяктуу так илимдер кызыктырабы?",
        "🤖 Сиз технологияга, электроникага же роботторго кызыгасызбы?",
        "🏛️ Архитектурага, интерьерге же курулушка кызыгасызбы?",
        "📱 Сиз мобилдик тиркемелерди, веб-сайттарды же оюндарды түзгүңүз келеби?",
        "🧩 Сиз алгоритмдерди, логиканы жана программалардын түзүмүн түшүнгөндү жактырасызбы?",
        "🔧 Сиз механизмдердин, жабдуулардын же роботтордун иштешине кызыгасызбы?",
        "🎮 Сиз өз оюндарыңызды, симуляцияларыңызды же VR дүйнөлөрүңүздү түзгүңүз келеби?",
        "🌐 Интернет тармактары, маалыматтык коопсуздук жана киберкоопсуздук кандай иштейт деп ойлонуп жатасызбы?"
    ]),
    ("Экономика, бизнес жана менеджмент институту", [
        "📊 Сиз маалыматтарды талдап, сандар менен иштөөнү жактырасызбы?",
        "💰 Экономика, каржы же бизнесте карьера кургуңуз келеби?",
        "📈 Сиз бизнес стратегияларына, долбоорлорду башкарууга же стартаптарга кызыгасызбы?",
        "📦 Сиз логистиканы, жеткирүү процесстерин же кампаны автоматташтырууну оптималдаштыргыңыз келеби?",
    ]),
    ("Медицина факультети", [
        "🩺 Сиз медицинага, ден соолукка же биотехнологияга кызыгасызбы?",
        "🏥 Сиз анатомияны, физиологияны жана медицинанын негиздерин үйрөнүүгө даярсызбы?",
        "🧬 Биологияга, генетикага же биомедицинага кызыгасызбы?"
    ]),
    ("Педагогика, искусство жана журналистика институту", [
        "🤝 Адамдарга жашоодогу же психологиялык кыйынчылыктарды чечүүгө жардам бергиңиз келеби?",
        "🎨 Сизди чыгармачылыкка, искусствого же дизайнга тартып жатабы?",
        "👩‍🏫Билим менен бөлүшүү жана башкаларга үйрөтүү сизге жагабы?",
        "🎥 Сизди медиа, кино, журналистика же эл алдында сүйлөгөн сөздөр кызыктырабы?",
        "🎤 Сиз эл алдында сүйлөп, презентацияларды жасаганга ыңгайлуусузбу?",
        "🧠 Сиз адамдын ой жүгүртүүсүнө кызыгасызбы жана ага кыйынчылыктар менен күрөшүүгө кантип жардам бере аласыз?",
        "👩‍🏫 Башкаларды үйрөтүп, мугалим же насаатчы болууну каалайсызбы?",
        "🎨 Интерфейстерди, визуалдык стилди же графиканы иштеп чыгууну каалайсызбы?"
    ]),

    ("Эл аралык билим берүү программаларынын жогорку мектеби", [
        "🌍 Эл аралык долбоорлорго катышкыңыз келеби же чет өлкөдө иштегиңиз келеби?",
        "🌏 Сиз дипломатияда иштегиңиз келеби, эл аралык сүйлөшүүлөргө катышкыңыз келеби же геосаясатты изилдегиңиз келеби?",
    ]),
    ("Филология жана маданиятаралык коммуникация институту", [
        "🈴 Сиз башка өлкөлөрдүн чет тилдерин жана маданиятын үйрөнүүнү жактырасызбы?",
        "📚 Сизге олуттуу адабияттарды үйрөнүү жана изилдөө жүргүзүү жагабы?",
        "📝 Сиз жазууга кызыгасызбы: эсселер, макалалар, окуялар, блогдор (акыркы суроо: ботко жоопторуңузду иштеп чыгууга убакыт (бир-эки секунд) бериңиз)?"
    ])
]:
    
    for q_kyrg in questions_kyrg:
        question_fields_kyrg.append((q_kyrg, faculty_kyrg))


class CareerTestKyrg(StatesGroup):
    q_index = State()
    answers = State()

def yes_no_kb_kyrg(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ооба", callback_data=f"yes_kyrg_{index}"),
         InlineKeyboardButton(text="Жок", callback_data=f"no_kyrg_{index}")]
    ])

from stud_reg import is_admin
from database import is_registered

@router_kyrg.message(F.text == "🔍 Кесип тандоо")
async def start_test_kerg(message: types.Message, state: FSMContext):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Боттун мүмкүнчүлүктөрүн пайдалануу үчүн катталыңыз.", reply_markup=keyboard_3_kyrg)
        return

    await message.answer(question_fields_kyrg[0][0], reply_markup=yes_no_kb_kyrg(0))
    await state.update_data(q_index=0, answers=[], lang="kg")
    await state.set_state(CareerTestKyrg.q_index)

@router_kyrg.callback_query(lambda c: c.data.startswith(("yes_kyrg_", "no_kyrg_")))
async def handle_answer_kyrg(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data.get("q_index", 0)
    answers = data.get("answers", [])

    current_index = int(callback.data.split("_")[1])
    if current_index != index:
        await callback.answer()
        return

    if callback.data.startswith("yes_kyrg"):
        answers.append(question_fields_kyrg[index][1])

    index += 1

    if index < len(question_fields_kyrg):
        await state.update_data(q_index=index, answers=answers)
        question_text = question_fields_kyrg[index][0]
        await callback.message.edit_text(question_text, reply_markup=yes_no_kb_kyrg(index))
    else:
        await state.clear()
        interests = Counter(answers)
        

def generate_prompt_kyrg(interests):
    return (
        "Сиз кесипкөй карьера консультантысыз. Колдонуучунун жоопторуна таянып, ага эң ылайыктуу адистиктерди сунуштаңыз. "
        "Чыгаруу форматы:\n\n"
        "1. Адегенде 3-5 эң ылайыктуу институттарды/факультеттерди кызыкчылыкка жараша иреттеңиз\n"
        "2. Ар бир институт үчүн 2-3 эң ылайыктуу адистиктерди көрсөтүңүз\n"
        "3. Кыскача түшүндүрмө берүү (1 сүйлөм)\n"
        "4. Берилген тизмеден гана адистиктерди колдонуңуз\n\n"
        "Колдонуучунун кызыкчылыктары:\n"
        f"{', '.join(interests)}\n\n"
        "Жеткиликтүү институттар жана адистиктер:\n"
        "\n".join([f"🎓 *{k}*:\n   - " + "\n   - ".join(v) for k, v in specialties_kyrg.items()]) +
        "\n\n"
        "Жообуңузду төмөнкүдөй форматтаңыз:\n"
        "🏛 *Институттун аталышы*\n"
        "   ✨ Адистик 1 (кыскача түшүндүрмө)\n"
        "   ✨ Адистик 2 (кыскача түшүндүрмө)\n"
        "   ...\n\n"
        "Кыска, так жана берилген маалыматтарды гана колдонуңуз. Answer using only Kyrgyz language"
    )

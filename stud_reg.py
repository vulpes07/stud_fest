import os, sys, sqlite3, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup

router = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  
if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")

DB_PATH = "bot_db.sqlite3"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL,  
                    age INTEGER NOT NULL,  
                    gender TEXT, 
                    ph_num INTEGER NOT NULL,    
                    latitude REAL,
                    longitude REAL,
                    user_id INTEGER,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT
                        
                );
            """)
            conn.commit()


def is_registered(user_id: int) -> bool:
    return user_id in [user[7] for user in list_users()]


def add_user(name: str, age: int, gender: str, ph_num: int, latitude: float, longitude: float, user_id: int = None, first_name: str = "", last_name: str = "", username: str = ""):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("INSERT INTO users (name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                         (name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username))

def list_users():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        return conn.execute("SELECT id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username FROM users").fetchall()

def remove_user(id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("DELETE FROM users WHERE id = ?", (id,))
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить локацию", request_location=True)],
    ],
    resize_keyboard=True
)


menu_2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Подобрать профессию")],
    ],
    resize_keyboard=True
)


@router.message(Command("info"))
async def info_command(message: types.Message):
    

    response_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Зарегистрироваться")],
            [KeyboardButton(text="🔍 Подобрать профессию")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Список доступных команд: ", reply_markup=response_menu)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class FSMAdminAdd(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    latitude = State()
    longitude = State()

class FSMAdminDel(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Подобрать профессию")],
            [KeyboardButton(text="➕ Добавить пользователя")],
            [KeyboardButton(text="📋 Список пользователей")],
            [KeyboardButton(text="❌ Удалить пользователя")]
        ],
        resize_keyboard=True
    )
    keyboard_2 = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Зарегистрироваться")]
        ],
        resize_keyboard=True
    )
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Привет, {message.from_user.first_name}! Это панель для администратора.\n"
            "📋Доступные команды:",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            f"""👋 Привет, {message.from_user.first_name}! Вас приветствует бот для определения подходящей для вас профессии которым обучают в ОШгу. Перед тем как воспользоваться функциями бота, пройдите регистрацию. А если уже прошли регистрацию, нажмите на /info .

По всем дополнительным вопросам обращайтесь к создателю бота: @vulpes_07.

Подробная информация о специальностях и поступлении на этом сайте: https://www.oshsu.kg/ru/page/56

Выберите действие:""",
            reply_markup=keyboard_2
        )

@router.message(F.text == "➕ Добавить пользователя")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await start_add_user(message, state)

@router.message(F.text == "➕ Зарегистрироваться")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await start_add_user(message, state)

@router.message(F.text == "📋 Список пользователей")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router.message(F.text == "❌ Удалить пользователя")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(FSMAdminAdd.name)


@router.message(FSMAdminAdd.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите свой возраст:")
    await state.set_state(FSMAdminAdd.age)

@router.message(FSMAdminAdd.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAdd.gender) 
    await message.answer("Выберите пол:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужчина", callback_data="gender_male")],
        [InlineKeyboardButton(text="Женщина", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAdd.gender)

@router.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Мужчина" if callback_query.data == "gender_male" else "Женщина"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Введите номер телефона:")
    await state.set_state(FSMAdminAdd.ph_num)

@router.message(FSMAdminAdd.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер телефона.")
        return
    await state.update_data(ph_num=int(message.text))
    await message.answer(f"{message.from_user.full_name}, отправьте вашу геолокацию.", reply_markup=menu)
    await state.set_state(FSMAdminAdd.latitude)

@router.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"Произошла ошибка: отсутствует поле {field}. Попробуйте заново начать регистрацию.")
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
    await message.answer(f"Ваши данные успешно добавлены! Спасибо за регистрацию, можете воспользоваться функциями бота",  reply_markup=menu_2)
    await state.clear()  

@router.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return
    users = list_users()
    if not users:
        await message.answer("В базе данных нет пользователей.")
        return

    response = "\n".join([f"""
{id}. {name} 
Возраст: {age}
Пол: {gender}
Номер телефона {ph_num}  
Локация: широта: {latitude}, долгота: {longitude}
username: @{username if username else '-'}
Имя и фамилия указанная пользователем в тг: {first_name} {last_name}
ID пользователя: {user_id}""" 
                          for id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username in users])
    await message.answer(f"Список пользователей:\n{response}")



@router.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("В базе данных нет пользователей для удаления.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Выберите пользователя для удаления:", reply_markup=kb)


@router.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])

    remove_user(user_id)

    await callback_query.message.edit_text(f"✅ Пользователь {user_id} удалён.")
    await callback_query.answer("Пользователь успешно удалён!")

    await state.clear()
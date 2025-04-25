from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# 1 реплай клавиатура после регистрации 

menu_2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Подобрать профессию")],
    ],
    resize_keyboard=True
)

menu_2_kyrg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Кесип тандоо")],
    ],
    resize_keyboard=True
)


menu_2_germ = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Berufe auswählen")],
    ],
    resize_keyboard=True
)


menu_2_eng = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Choose professions")],
    ],
    resize_keyboard=True
)

# 2 клавиатура после вопроса про номер, на вопросе про локацию

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить локацию", request_location=True)],
    ],
    resize_keyboard=True
)



menu_kyrg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Локация жөнөтүү", request_location=True)],
    ],
    resize_keyboard=True
)


menu_germ = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Senden Sie den Standort", request_location=True)],
    ],
    resize_keyboard=True
)


menu_eng = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Send the location", request_location=True)],
    ],
    resize_keyboard=True
)



# Клавиатура для команды /info
response_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Зарегистрироваться")],
            [KeyboardButton(text="🛠 Админ-панель")],
            [KeyboardButton(text="🔍 Подобрать профессию")]
        ],
        resize_keyboard=True
    )



response_menu_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin panel")],
            [KeyboardButton(text="➕ Registrieren")],
            [KeyboardButton(text="🔍 Berufe auswählen")]
        ],
        resize_keyboard=True
    )


response_menu_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin Panel")],
            [KeyboardButton(text="➕ Register")],
            [KeyboardButton(text="🔍 Choose professions")]
        ],
        resize_keyboard=True
    )


response_menu_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ панель")],
            [KeyboardButton(text="➕ Катталуу")],
            [KeyboardButton(text="🔍 Кесип тандоо")]
        ],
        resize_keyboard=True
    )
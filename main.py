import os, sys, asyncio, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext


from stud_reg import router, init_db, cmd_start_rus
from career_test import router_test
from kyrg import router_kyrg, cmd_start_kyrg
from germ import router_germ, cmd_start_germ
from eng import router_eng, cmd_start_eng  

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")

ADMIN_ID = int(ADMIN_ID)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_kg"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de")
    ]
])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Выберите язык 🌍:\n"
        "Тилди тандаңыз 🌍:\n"
        "Choose the language 🌍:\n"
        "Wählen Sie die Sprache 🌍:",
        reply_markup=language_keyboard
    )

@dp.callback_query(F.data.startswith("lang_"))
async def handle_language(callback: CallbackQuery, state: FSMContext):  
    lang = callback.data.replace("lang_", "")
    await callback.message.delete()

    await state.update_data(lang=lang)
    
    if lang == "ru":
        await cmd_start_rus(callback.message)
    elif lang == "kg":
        await cmd_start_kyrg(callback.message)
    elif lang == "en":
        await cmd_start_eng(callback.message)
    elif lang == "de":
        await cmd_start_germ(callback.message)

async def main():
    init_db()
    dp.include_router(router)
    dp.include_router(router_test)
    dp.include_router(router_kyrg)
    dp.include_router(router_eng)
    dp.include_router(router_germ)
    print("Бот запущен!")

    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass
    finally:
        print("Бот завершил работу!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())



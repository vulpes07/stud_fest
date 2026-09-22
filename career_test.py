from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
router_test = Router()
import os,httpx,sys
from collections import Counter
from dotenv import load_dotenv
from stud_reg import is_admin
keyboard_3 = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Зарегистрироваться")]
        ],
        resize_keyboard=True)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  
if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")



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
    

specialties = {
    "ИНСТИТУТ ФИЛОЛОГИИ И МЕЖКУЛЬТУРНОЙ КОММУНИКАЦИИ":[
    "Кыргызский язык и литература",
    "Государственный язык в учреждениях образования с некыргызским языком обучения",
    "Русский язык и литература",
    "Английский язык",
    "Немецкий язык",
    "Французский язык",
    "Корейский язык",
    "Лингвистика: Перевод и переводоведение",
    "Лингвистика: Теория и методика преподавания иностранных языков и культур"
    ],
    "ИНСТИТУТ ПЕДАГОГИКИ, ИСКУССТВА И ЖУРНАЛИСТИКИ":[
    "Начальное образование",
    "Дошкольное образование и логопедия",
    "Психология",
    "Художественное образование",
    "Музыкальное искусство",
    "Изобразительное искусство",
    "Музыкальное искусство эстрады",
    "Дизайн: дизайн костюма, дизайн интерьера",
    "Искусство костюма и текстиля",
    "Актерское искусство",
    "Режиссура (Кино, ТВ)",
    "Кинооператорство (Кино, ТВ)",
    "Журналистика",
    "Реклама и связи с общественностью"
    ],
    "ИСТОРИКО-ЮРИДИЧЕСКИЙ ИНСТИТУТ": [
    "Социально-экономическое образование: История",
    "Библиотековедение и документоведение",
    "Юриспруденция",
    "Таможенное дело",
    "Судебная экспертиза"
    ],
    "ИНСТИТУТ ЕСТЕСТВОЗНАНИЯ, ФИЗИЧЕСКОГО ВОСПИТАНИЯ, ТУРИЗМА И АГРАРНЫХ ТЕХНОЛОГИЙ":[
    "Естественно-научное образование: Биология",
    "Естественно-научное образование: Химия",
    "Естественно-научное образование: География",
    "Биология (Биология; Биология и лабораторная работа)",
    "Химия (профиль: химико-экологическая, криминалистическая экспертиза)",
    "География",
    "Туризм",
    "Агрономия (профиль: защита карантинных растений)",
    "Ветеринария",
    "Прикладная геодезия",
    "Физическая культура и спорт"
    ],
    "ИНСТИТУТ МАТЕМАТИКИ, ФИЗИКИ, ТЕХНИКИ И ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ": [
    "Физико-математическое образование: Математика и информатика",
    "Физико-математическое образование: Физика",
    "Прикладная математика и информатика",
    "Big Data аналитика",
    "Прикладная информатика в экономике",
    "Прикладная информатика в архитектуре",
    "Автоматизированное управление бизнес-процессами и финансами",
    "Программное обеспечение вычислительной техники и автоматизированных систем (ПОВТАС)",
    "Автоматизированные системы обработки информации и управления (АСОИУ)",
    "Информационные системы и технологии в экономике",
    "Информационные системы и технологии в образовании",
    "Информационная безопасность",
    "Информатика в здравоохранении и биомедицинская инженерия",
    "Математическое обеспечение и администрирование информационных систем",
    "Веб-технологии и программное обеспечение мобильных систем",
    "Разработка программ для управления электромобилями и робототехническими системами",
    "Математика и системный анализ",
    "Компьютерная лингвистика",
    "Дизайн: графический дизайн",
    "Электроснабжение",
    "Агроинженерия",
    "Архитектура",
    "Техническая физика: Медицинская физика",
    "Техническая физика: Физические методы криминалистической экспертизы",
    "Мехатроника и робототехника"
    ],

    "ИНСТИТУТ ЭКОНОМИКИ, БИЗНЕСА И МЕНЕДЖМЕНТА": [
    "Экономика: Финансы и кредит",
    "Экономика: Бухгалтерский учет, анализ и аудит",
    "Экономика: Экономика и управление на предприятии",
    "Экономика: Налог и налогообложение",
    "Экономика: IT-Бухгалтерия",
    "Экономика: Цифровая экономика и математические методы",
    "Экономика: Аудит и финансовый контроль",
    "Экономика: Финансовый аналитик в бизнесе",
    "Экономика: Финансовая безопасность и финансовый контроль",
    "Маркетинг",
    "Бизнес информатика",
    "Бизнес управление",
    "Государственное и муниципальное управление",
    "Социальная работа"
    ],

    "ИНСТИТУТ ВОСТОКОВЕДЕНИЯ": [
    "Востоковедение: Восточные языки и дипломатия",
    "Востоковедение: История Востока –с преподаванием восточных языков",
    "Филология: Восточные языки",
    "Лингвистика: Перевод и переводоведение: Восточные языки",
    "Конфликтология: Общая конфликтология"
    ],

    "ВЫСШАЯ ШКОЛА МЕЖДУНАРОДНЫХ ОБРАЗОВАТЕЛЬНЫХ ПРОГРАММ": [
    "Регионоведение: Восточная Азия",
    "Начальное образование. Английский язык",
    "Математика и компьютерные науки",
    "Компьютерное моделирование в инженерном и технологическом проектировании",
    "Цифровая дипломатия в международных отношениях",
    "Интернет технологии и управление",
    "Экономика: Мировая экономика",
    "Европоведение",
    "Бизнес управление: Международный бизнес",
    "Английский язык с дополнительной профилю: Перевод и переводоведение",
    "Английский язык с дополнительной профилю: Компьютерная лингвистика",
    "Международные отношения",
    "Мировая интеграция и международные организации",
    "Политология"
    ],

    "КЫРГЫЗСКО-КИТАЙСКИЙ ФАКУЛЬТЕТ": [
    "Китаеведение",
    "Лингвистика: Перевод и переводоведение",
    "Информатика и технологии",
    "Электронная информационная инженерия",
    "Филология: Методика преподавания филологических дисциплин (Английский язык, Китайский язык)"
    ],
    "МЕДИЦИНСКИЙ ФАКУЛЬТЕТ": [
    "Лечебное дело",
    "Педиатрия",
    "Медико-профилактическое дело",
    "Стоматология",
    "Фармация",
    "Сестринское дело",
    "Лабораторное дело",
    ],
    "ТЕОЛОГИЧЕСКИЙ ФАКУЛЬТЕТ": [
    "Теология"],

    "ГУМАНИТАРНЫЙ ИНСТИТУТ АРАШАН": [
    "Теология"]
}
question_fields = []
for faculty, questions in [
    ("Институт математики, физики, техники и информационных технологий", [
        "🧠 Любишь ли ты решать логические задачи и головоломки?",
        "💻 Интересуешься ли ты программированием или цифровыми технологиями?",
        "🔬 Привлекают ли тебя точные науки, такие как математика и физика?",
        "🤖 Увлекаешься ли ты техникой, электроникой или роботами?",
        "🏛️ Интересуешься архитектурой, интерьерами или строительством?",
        "📱 Хочешь ли ты создавать мобильные приложения, сайты или игры?",
        "🧩 Любишь разбираться в алгоритмах, логике и структуре программ?",
        "🔧 Интересуешься ли ты работой механизмов, техникой или роботами?",
        "🎮 Хотел бы ты создавать собственные игры, симуляции или VR-миры?",
        "🌐 Интересно ли тебе, как устроены интернет-сети, защита информации и кибербезопасность?"
    ]),
    ("Институт экономики, бизнеса и менеджмента", [
        "📊 Нравится ли тебе анализировать данные и работать с числами?",
        "💰 Хочешь ли ты построить карьеру в экономике, финансах или бизнесе?",
        "📈 Интересуешься ли ты бизнес-стратегиями, управлением проектами или стартапами?",
        "📦 Хотел бы ты оптимизировать логистику, процессы поставок или автоматизацию складов?"
    ]),
    ("Медицинский факультет", [
        "🩺 Интересуешься ли ты медициной, здоровьем или биотехнологиями?",
        "🏥 Готов ли ты изучать анатомию, физиологию и основы медицины?",
        "🧬 Есть ли у тебя интерес к биологии, генетике или биомедицине?"
    ]),
    ("Институт педагогики, искусства и журналистики", [
        "🤝 Хочешь ли ты помогать людям решать их жизненные или психологические трудности?",
        "🎨 Тянет ли тебя к творчеству, искусству или дизайну?",
        "👩‍🏫 Нравится ли тебе делиться знаниями и обучать других?",
        "🎥 Привлекает ли тебя медиа, кино, журналистика или публичные выступления?",
        "🎤 Тебе комфортно выступать публично, вести презентации?",
        "🧠 Интересуешься ли ты тем, как мыслит человек, и как помочь ему справиться с трудностями?",
        "👨‍🏫 Есть ли у тебя желание обучать других и становиться преподавателем или наставником?",
        "🎨 Хотел бы ты разрабатывать интерфейсы, визуальный стиль или графику?"
    ]),
    ("Высшая школа международных образовательных программ", [
        "🌍 Хотел бы ты участвовать в международных проектах или работать за рубежом?",
        "🌏 Хотел бы ты работать в дипломатии, участвовать в международных переговорах или изучать геополитику?"
    ]),
    ("Институт филологии и межкультурной коммуникации", [
        "🈴 Любишь ли ты изучать иностранные языки и культуру других стран?",
        "📚 Нравится ли тебе изучать серьёзную литературу, проводить исследования?",
        "📝 Увлекаешься ли ты письмом: эссе, статьи, рассказы, блоги (последний вопрос - дайте боту время (пару секунд) чтобы обработать ваши ответы)?"
    ])
]:
    for q in questions:
        question_fields.append((q, faculty))

class CareerTest(StatesGroup):
    q_index = State()
    answers = State()

def yes_no_kb(index: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"yes_{index}"),
         InlineKeyboardButton(text="Нет", callback_data=f"no_{index}")]
    ])

from stud_reg import is_admin
from database import is_registered

@router_test.message(F.text == "🔍 Подобрать профессию")
async def start_test(message: types.Message, state: FSMContext):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Пройдите регистрацию, чтобы воспользоваться функциями бота.", reply_markup=keyboard_3)
        return

    await message.answer(question_fields[0][0], reply_markup=yes_no_kb(0))
    await state.update_data(q_index=0, answers=[], lang="ru")
    await state.set_state(CareerTest.q_index)

from eng import question_fields_eng, yes_no_kb_eng, generate_prompt_eng
from germ import question_fields_germ, yes_no_kb_germ, generate_prompt_germ
from kyrg import question_fields_kyrg, yes_no_kb_kyrg, generate_prompt_kyrg


@router_test.callback_query(lambda c: c.data.startswith(("yes_", "no_", "yes_eng_", "no_eng_", "yes_germ_", "no_germ_", "yes_kyrg_", "no_kyrg_")))
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if lang == "en":
        questions = question_fields_eng
        kb_func = yes_no_kb_eng
    elif lang == "de":
        questions = question_fields_germ
        kb_func = yes_no_kb_germ
    elif lang == "kg":
        questions = question_fields_kyrg
        kb_func = yes_no_kb_kyrg
    else:
        questions = question_fields
        kb_func = yes_no_kb




    index = data.get("q_index", 0)
    answers = data.get("answers", [])


    parts = callback.data.split("_")
    if len(parts) == 2:  
        current_index = int(parts[1])
    elif len(parts) == 3:  
        current_index = int(parts[2])
    else:
        await callback.answer()
        return

    if current_index != index:
        await callback.answer()
        return

    if callback.data.startswith(("yes", "yes_eng", "yes_germ", "yes_kyrg")):
        answers.append(question_fields[index][1])

    index += 1

    if index < len(question_fields):
        await state.update_data(q_index=index, answers=answers)
        question_text = questions[index][0]
        await callback.message.edit_text(question_text, reply_markup=kb_func(index))

    else:
        await state.clear()
        interests = Counter(answers)
    

        prompt = (
    "Ты — профессиональный карьерный консультант. На основе ответов пользователя определи наиболее подходящие специальности. "
    "Формат вывода:\n\n"
    "1. Сначала укажи 3-5 самых релевантных институтов/факультетов в порядке убывания соответствия интересам\n"
    "2. Для каждого института выдели 2-3 самые подходящие специальности\n"
    "3. Объясни кратко (1 предложение), почему эти специальности подходят\n"
    "4. Используй только специальности из предоставленного списка\n\n"
    "Интересы пользователя:\n"
    f"{', '.join(interests)}\n\n"
    "Доступные институты и специальности:\n"
    "\n".join([f"🎓 *{k}*:\n   - " + "\n   - ".join(v) for k, v in specialties.items()]) +
    "\n\n"
    "Форматируй ответ так:\n"
    "🏛 *Название института*\n"
    "   ✨ Специальность 1 (краткое объяснение)\n"
    "   ✨ Специальность 2 (краткое объяснение)\n"
    "   ...\n\n"
    "Будь кратким, конкретным и используй только предоставленные данные. Answer using only Russian language"
)


        lang = data.get("lang", "ru")


        if lang == "en":
            try:
                prompt = generate_prompt_eng(interests) 
                response = await ask_mistral(prompt)
                await callback.message.edit_text(f"🤖 I am convinced that:\n\n{response}")
            except Exception as e:
                await callback.message.edit_text("Ошибка при обращении к нейросети.")

        elif lang == "de":
            try:
                prompt = generate_prompt_germ(interests)
                response = await ask_mistral(prompt)
                await callback.message.edit_text(f"🤖 Ich glaube, das:\n\n{response}")
            except Exception as e:
                await callback.message.edit_text("Ошибка при обращении к нейросети.")

        elif lang == "kg":
            try:
                prompt = generate_prompt_kyrg(interests)  
                response = await ask_mistral(prompt)
                await callback.message.edit_text(f"🤖 Мен ушундай деп ойлойм:\n\n{response}")
            except Exception as e:
                await callback.message.edit_text("Ошибка при обращении к нейросети.")
        else:
            try:
                response = await ask_mistral(prompt)
                await callback.message.edit_text(f"🤖 Вот что я думаю:\n\n{response}")
            except Exception as e:
                await callback.message.edit_text("Ошибка при обращении к нейросети.")

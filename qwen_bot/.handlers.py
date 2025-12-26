from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_db_connection
from states import SurveyStates

router = Router()

# --- Вспомогательные функции ---

def save_response(user_id: int, **kwargs):
    # Ничего не делаем, если нет данных для сохранения
    if not kwargs:
        return

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Проверяем, существует ли уже запись
        cursor.execute("SELECT 1 FROM responses WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone() is not None

        if exists:
            # Обновляем только указанные поля
            set_clause = ", ".join([f"{key} = ?" for key in kwargs])
            values = list(kwargs.values()) + [user_id]
            query = f"UPDATE responses SET {set_clause} WHERE user_id = ?"
            cursor.execute(query, values)
        else:
            # Вставляем новую запись (все поля, кроме user_id, могут быть NULL)
            keys = ["user_id"] + list(kwargs.keys())
            placeholders = ["?"] * len(keys)
            values = [user_id] + list(kwargs.values())
            query = f"INSERT INTO responses ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)

        conn.commit()

# --- Команда /survey ---

@router.message(Command("survey"))
async def start_survey(message: Message, state: FSMContext):
    # Сохраняем начальную запись (на всякий случай)
    save_response(message.from_user.id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="до 16"), KeyboardButton(text="16-18"), KeyboardButton(text="18+")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сколько вам лет?", reply_markup=keyboard)
    await state.set_state(SurveyStates.age)

# --- Возраст ---

@router.message(SurveyStates.age, F.text.in_({"до 16", "16-18", "18+"}))
async def process_age(message: Message, state: FSMContext):
    age_group = message.text
    user_id = message.from_user.id
    save_response(user_id, age_group=age_group)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Москва"), KeyboardButton(text="Другой")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("В каком городе вы живёте?", reply_markup=keyboard)
    await state.set_state(SurveyStates.city_choice)

@router.message(SurveyStates.age)
async def invalid_age(message: Message):
    await message.answer("Пожалуйста, выберите один из вариантов.")

# --- Выбор города ---

@router.message(SurveyStates.city_choice, F.text == "Москва")
async def city_moscow(message: Message, state: FSMContext):
    user_id = message.from_user.id
    save_response(user_id, city="Москва")

    # ❌ НЕ завершаем анкету!
    # ✅ Переходим к следующему шагу — названию экзамена
    await message.answer("Введите название экзамена (минимум 3 буквы):")
    await state.set_state(SurveyStates.exam_name)


@router.message(SurveyStates.city_choice, F.text == "Другой")
async def city_other(message: Message, state: FSMContext):
    await message.answer("Введите название города (минимум 3 буквы):")
    await state.set_state(SurveyStates.city_input)

@router.message(SurveyStates.city_choice)
async def invalid_city_choice(message: Message):
    await message.answer("Пожалуйста, выберите 'Москва' или 'Другой'.")

# --- Ввод названия города ---

@router.message(SurveyStates.city_input)
async def process_city_input(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city.isalpha() or len(city) < 3:
        await message.answer("Название города должно содержать только буквы и быть не короче 3 символов. Попробуйте снова:")
        return

    user_id = message.from_user.id
    save_response(user_id, city=city)

    # ❌ НЕ завершаем анкету!
    # ✅ Переходим к следующему шагу — названию экзамена
    await message.answer("Введите название экзамена (минимум 3 буквы):")
    await state.set_state(SurveyStates.exam_name)

# --- Название экзамена ---
@router.message(SurveyStates.city_input)
async def process_city_input(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city.isalpha() or len(city) < 3:
        await message.answer("Название города должно содержать только буквы и быть не короче 3 символов. Попробуйте снова:")
        return

    user_id = message.from_user.id
    save_response(user_id, city=city)

    await message.answer("Введите название экзамена (минимум 3 буквы):")
    await state.set_state(SurveyStates.exam_name)

# --- Название экзамена (ввод) ---
@router.message(SurveyStates.exam_name)
async def process_exam_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("Название экзамена должно быть не короче 3 символов. Попробуйте снова:")
        return

    user_id = message.from_user.id
    save_response(user_id, exam_name=name)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Тест"), KeyboardButton(text="Задачи")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите тип экзамена:", reply_markup=keyboard)
    await state.set_state(SurveyStates.exam_type)

# --- Тип экзамена ---
@router.message(SurveyStates.exam_type, F.text.in_({"Тест", "Задачи"}))
async def process_exam_type(message: Message, state: FSMContext):
    exam_type = message.text
    user_id = message.from_user.id
    save_response(user_id, exam_type=exam_type)

    if exam_type == "Тест":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Множественный выбор")],
                [KeyboardButton(text="Один из нескольких")],
                [KeyboardButton(text="Кейс и вопросы по нему")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Выберите тип теста:", reply_markup=keyboard)
        await state.set_state(SurveyStates.test_subtype)
    else:  # "Задачи"
        # Пропускаем подтип теста
        save_response(user_id, test_subtype=None)
        await message.answer("Введите количество заданий в экзамене (целое число):")
        await state.set_state(SurveyStates.task_count)

@router.message(SurveyStates.exam_type)
async def invalid_exam_type(message: Message):
    await message.answer("Пожалуйста, выберите 'Тест' или 'Задачи'.")

# --- Подтип теста (если "Тест") ---
@router.message(SurveyStates.test_subtype, F.text.in_({"Множественный выбор", "Один из нескольких", "Кейс и вопросы по нему"}))
async def process_test_subtype(message: Message, state: FSMContext):
    test_subtype = message.text
    user_id = message.from_user.id
    save_response(user_id, test_subtype=test_subtype)
    await message.answer("Введите количество заданий в экзамене (целое число):")
    await state.set_state(SurveyStates.task_count)

@router.message(SurveyStates.test_subtype)
async def invalid_test_subtype(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных типов теста.")

# --- Количество заданий ---
@router.message(SurveyStates.task_count)
async def process_task_count(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Пожалуйста, введите целое число (например, 10):")
        return
    task_count = int(text)
    if task_count <= 0:
        await message.answer("Количество заданий должно быть больше нуля.")
        return

    user_id = message.from_user.id
    save_response(user_id, task_count=task_count)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="45 минут"), KeyboardButton(text="1 час")],
            [KeyboardButton(text="полтора часа"), KeyboardButton(text="4 часа")],
            [KeyboardButton(text="Другой")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите время на решение:", reply_markup=keyboard)
    await state.set_state(SurveyStates.time_choice)

# --- Время на решение (выбор) ---
@router.message(SurveyStates.time_choice, F.text.in_({"45 минут", "1 час", "полтора часа", "4 часа"}))
async def process_time_choice(message: Message, state: FSMContext):
    time_map = {
        "45 минут": 45,
        "1 час": 60,
        "полтора часа": 90,
        "4 часа": 240
    }
    minutes = time_map[message.text]
    user_id = message.from_user.id
    save_response(user_id, time_minutes=minutes)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="одна"), KeyboardButton(text="несколько")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сколько попыток даётся для сдачи экзамена?", reply_markup=keyboard)
    await state.set_state(SurveyStates.attempts)

@router.message(SurveyStates.time_choice, F.text == "Другой")
async def time_custom_request(message: Message, state: FSMContext):
    await message.answer("Введите время на решение в минутах (целое число):")
    await state.set_state(SurveyStates.time_custom)

@router.message(SurveyStates.time_choice)
async def invalid_time_choice(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

# --- Ввод времени вручную ---
@router.message(SurveyStates.time_custom)
async def process_time_custom(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Пожалуйста, введите целое число минут:")
        return
    minutes = int(text)
    if minutes <= 0:
        await message.answer("Время должно быть больше нуля минут.")
        return

    user_id = message.from_user.id
    save_response(user_id, time_minutes=minutes)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="одна"), KeyboardButton(text="несколько")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сколько попыток даётся для сдачи экзамена?", reply_markup=keyboard)
    await state.set_state(SurveyStates.attempts)

# --- Проходной балл ---
@router.message(SurveyStates.attempts, F.text.in_({"одна", "несколько"}))
async def process_attempts(message: Message, state: FSMContext):
    attempts = message.text
    user_id = message.from_user.id
    save_response(user_id, attempts=attempts)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="отсутствует"), KeyboardButton(text="50%"), KeyboardButton(text="80%")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Укажите проходной балл:", reply_markup=keyboard)
    await state.set_state(SurveyStates.passing_score)

@router.message(SurveyStates.attempts)
async def invalid_attempts(message: Message):
    await message.answer("Пожалуйста, выберите 'одна' или 'несколько'.")


# --- Проходной балл: выбор ---
@router.message(SurveyStates.passing_score, F.text.in_({"отсутствует", "50%", "80%"}))
async def process_passing_score(message: Message, state: FSMContext):
    passing_score = message.text
    user_id = message.from_user.id
    save_response(user_id, passing_score=passing_score)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="зачёт"), KeyboardButton(text=">90%"), KeyboardButton(text="100%")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Какой результат требуется?", reply_markup=keyboard)
    await state.set_state(SurveyStates.required_result)

@router.message(SurveyStates.passing_score)
async def invalid_passing_score(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")


# --- Требуемый результат ---
@router.message(SurveyStates.required_result, F.text.in_({"зачёт", ">90%", "100%"}))
async def process_required_result(message: Message, state: FSMContext):
    required_result = message.text
    user_id = message.from_user.id
    save_response(user_id, required_result=required_result)

    await message.answer("Введите дату экзамена (например, 15.06.2025 или как вам удобно):")
    await state.set_state(SurveyStates.exam_date)

@router.message(SurveyStates.required_result)
async def invalid_required_result(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")


# --- Дата экзамена (свободный ввод) ---
@router.message(SurveyStates.exam_date)
async def process_exam_date(message: Message, state: FSMContext):
    exam_date = message.text.strip()
    if len(exam_date) < 4:  # минимальная разумная длина
        await message.answer("Пожалуйста, введите дату (например: 10.12.2025):")
        return

    user_id = message.from_user.id
    save_response(user_id, exam_date=exam_date)

    # Важность — фиксированный вариант (по ТЗ: только один)
    # Но сделаем кнопкой для единообразия
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="От экзамена зависит работа, учёба, судьба")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Насколько важен экзамен?", reply_markup=keyboard)
    await state.set_state(SurveyStates.importance)

# --- Важность: выбор из трёх вариантов ---
@router.message(SurveyStates.exam_date)
async def process_exam_date(message: Message, state: FSMContext):
    exam_date = message.text.strip()
    if len(exam_date) < 4:  # минимальная разумная длина
        await message.answer("Пожалуйста, введите дату (например: 10.12.2025):")
        return

    user_id = message.from_user.id
    save_response(user_id, exam_date=exam_date)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="работа"), KeyboardButton(text="учёба")],
            [KeyboardButton(text="судьба")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("От экзамена зависит:", reply_markup=keyboard)
    await state.set_state(SurveyStates.importance)


@router.message(SurveyStates.importance, F.text.in_({"работа", "учёба", "судьба"}))
async def process_importance(message: Message, state: FSMContext):
    importance = message.text
    user_id = message.from_user.id
    save_response(user_id, importance=importance)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="да"), KeyboardButton(text="нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Есть ли примеры экзаменационных заданий?", reply_markup=keyboard)
    await state.set_state(SurveyStates.has_examples)


@router.message(SurveyStates.importance)
async def invalid_importance(message: Message):
    await message.answer("Пожалуйста, выберите один из вариантов: работа, учёба или судьба.")

# --- Наличие примеров ---
@router.message(SurveyStates.has_examples, F.text.in_({"да", "нет"}))
async def process_has_examples(message: Message, state: FSMContext):
    has_examples = message.text
    user_id = message.from_user.id
    save_response(user_id, has_examples=has_examples)

    await message.answer("Спасибо! Анкета успешно завершена.")
    await state.clear()

@router.message(SurveyStates.has_examples)
async def invalid_has_examples(message: Message):
    await message.answer("Пожалуйста, выберите 'да' или 'нет'.")
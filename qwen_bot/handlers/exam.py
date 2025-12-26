from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

router = Router()

# --- Название экзамена ---
@router.message(SurveyStates.exam_name)
async def process_exam_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("Название экзамена должно быть не короче 3 символов.")
        return
    save_response(message.from_user.id, exam_name=name)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Тест"), KeyboardButton(text="Задачи")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите тип экзамена:", reply_markup=keyboard)
    await state.set_state(SurveyStates.exam_type)

# --- Тип экзамена ---
@router.message(SurveyStates.exam_type, F.text.in_({"Тест", "Задачи"}))
async def process_exam_type(message: Message, state: FSMContext):
    exam_type = message.text
    save_response(message.from_user.id, exam_type=exam_type)
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
    else:
        save_response(message.from_user.id, test_subtype=None)
        await message.answer("Введите количество заданий в экзамене (целое число):")
        await state.set_state(SurveyStates.task_count)

@router.message(SurveyStates.exam_type)
async def invalid_exam_type(message: Message):
    await message.answer("Пожалуйста, выберите 'Тест' или 'Задачи'.")

# --- Подтип теста ---
@router.message(SurveyStates.test_subtype, F.text.in_({"Множественный выбор", "Один из нескольких", "Кейс и вопросы по нему"}))
async def process_test_subtype(message: Message, state: FSMContext):
    save_response(message.from_user.id, test_subtype=message.text)
    await message.answer("Введите количество заданий в экзамене (целое число):")
    await state.set_state(SurveyStates.task_count)

@router.message(SurveyStates.test_subtype)
async def invalid_test_subtype(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных типов теста.")

# --- Количество заданий ---
@router.message(SurveyStates.task_count)
async def process_task_count(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите целое положительное число.")
        return
    save_response(message.from_user.id, task_count=int(message.text))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="45 минут"), KeyboardButton(text="1 час")],
            [KeyboardButton(text="полтора часа"), KeyboardButton(text="4 часа")],
            [KeyboardButton(text="Другой")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("⏱️ Выберите время на прохождение всего экзамена:", reply_markup=keyboard)
    await state.set_state(SurveyStates.time_choice)

# --- Время: выбор ---
@router.message(SurveyStates.time_choice, F.text.in_({"45 минут", "1 час", "полтора часа", "4 часа"}))
async def process_time_choice(message: Message, state: FSMContext):
    time_map = {"45 минут": 45, "1 час": 60, "полтора часа": 90, "4 часа": 240}
    save_response(message.from_user.id, time_minutes=time_map[message.text])
    await _ask_attempts(message, state)

@router.message(SurveyStates.time_choice, F.text == "Другой")
async def time_custom_request(message: Message, state: FSMContext):
    await message.answer("⏱️ Введите время на решение в минутах (целое число):")
    await state.set_state(SurveyStates.time_custom)

@router.message(SurveyStates.time_choice)
async def invalid_time_choice(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

# --- Время: ввод ---
@router.message(SurveyStates.time_custom)
async def process_time_custom(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите целое положительное число минут.")
        return
    save_response(message.from_user.id, time_minutes=int(message.text))
    await _ask_attempts(message, state)

# --- Вспомогательная функция для единообразия ---
async def _ask_attempts(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="одна"), KeyboardButton(text="несколько")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сколько попыток даётся для сдачи экзамена?", reply_markup=keyboard)
    await state.set_state(SurveyStates.attempts)

# --- Попытки ---
@router.message(SurveyStates.attempts, F.text.in_({"одна", "несколько"}))
async def process_attempts(message: Message, state: FSMContext):
    save_response(message.from_user.id, attempts=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="отсутствует"), KeyboardButton(text="50%"), KeyboardButton(text="80%")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Укажите проходной балл:", reply_markup=keyboard)
    await state.set_state(SurveyStates.passing_score)

@router.message(SurveyStates.attempts)
async def invalid_attempts(message: Message):
    await message.answer("Пожалуйста, выберите 'одна' или 'несколько'.")

# --- Проходной балл ---
@router.message(SurveyStates.passing_score, F.text.in_({"отсутствует", "50%", "80%"}))
async def process_passing_score(message: Message, state: FSMContext):
    save_response(message.from_user.id, passing_score=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="зачёт"), KeyboardButton(text=">90%"), KeyboardButton(text="100%")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("🎯 Какой результат требуется?", reply_markup=keyboard)
    await state.set_state(SurveyStates.required_result)

@router.message(SurveyStates.passing_score)
async def invalid_passing_score(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

# --- Требуемый результат ---
@router.message(SurveyStates.required_result, F.text.in_({"зачёт", ">90%", "100%"}))
async def process_required_result(message: Message, state: FSMContext):
    save_response(message.from_user.id, required_result=message.text)
    await message.answer("Введите дату экзамена (например, 15.01.2026):")
    await state.set_state(SurveyStates.exam_date)

@router.message(SurveyStates.required_result)
async def invalid_required_result(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")

# --- Дата экзамена ---
@router.message(SurveyStates.exam_date)
async def process_exam_date(message: Message, state: FSMContext):
    if len(message.text.strip()) < 4:
        await message.answer("Пожалуйста, введите дату.")
        return
    save_response(message.from_user.id, exam_date=message.text.strip())
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="работа"), KeyboardButton(text="учёба")],
            [KeyboardButton(text="судьба"), KeyboardButton(text="не важен")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Насколько важен этот экзамен для вас? От экзамена зависит:", reply_markup=keyboard)
    await state.set_state(SurveyStates.importance)

# --- Важность ---
@router.message(SurveyStates.importance, F.text.in_({"не важен", "работа", "учёба", "судьба"}))
async def process_importance(message: Message, state: FSMContext):
    save_response(message.from_user.id, importance=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="да"), KeyboardButton(text="нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Есть ли примеры экзаменационных заданий?", reply_markup=keyboard)
    await state.set_state(SurveyStates.has_examples)

@router.message(SurveyStates.importance)
async def invalid_importance(message: Message):
    await message.answer("Пожалуйста, выберите: работа, учёба или судьба.")


# --- Примеры заданий ---
@router.message(SurveyStates.has_examples, F.text.in_({"да", "нет"}))
async def process_has_examples(message: Message, state: FSMContext):
    save_response(message.from_user.id, has_examples=message.text)

    # Переход к вопросам о рабочем месте
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="очно"), KeyboardButton(text="онлайн")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Где будет проходить экзамен?", reply_markup=keyboard)
    await state.set_state(SurveyStates.exam_location)

@router.message(SurveyStates.has_examples)
async def invalid_has_examples(message: Message):
    await message.answer("Пожалуйста, выберите 'да' или 'нет'.")
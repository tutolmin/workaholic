from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

router = Router()

# --- Запуск блока "Материалы" после завершения workspace ---
# Эту логику вызовет _finish_or_continue из workspace.py (см. ниже)

# --- 1. Есть ли материалы? ---
@router.message(SurveyStates.camera_count)  # последнее состояние workspace
async def after_workspace(message: Message, state: FSMContext):
    # На этом этапе workspace уже завершён
    # Переходим к материалам
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="да"), KeyboardButton(text="нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("У вас есть материалы для подготовки к экзамену?", reply_markup=keyboard)
    await state.set_state(SurveyStates.materials_exist)

# Если в workspace был короткий путь (например, очно → сразу завершение),
# то нужно также обрабатывать переход из других точек.
# Но для простоты предположим, что все проходят полную цепочку.


# --- 2. Есть / нет материалы ---
@router.message(SurveyStates.materials_exist, F.text.in_({"да", "нет"}))
async def process_materials_exist(message: Message, state: FSMContext):
    materials_exist = message.text
    user_id = message.from_user.id
    save_response(user_id, materials_exist=materials_exist)

    if materials_exist == "нет":
        # Нет материалов → завершаем анкету
        await _finish_survey(message, state)
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="оцифрованные"), KeyboardButton(text="на бумаге")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("В каком формате у вас материалы?", reply_markup=keyboard)
        await state.set_state(SurveyStates.materials_format)

@router.message(SurveyStates.materials_exist)
async def invalid_materials_exist(message: Message):
    await message.answer("Пожалуйста, выберите 'да' или 'нет'.")


# --- 3. Формат материалов ---
@router.message(SurveyStates.materials_format, F.text.in_({"оцифрованные", "на бумаге"}))
async def process_materials_format(message: Message, state: FSMContext):
    materials_format = message.text
    user_id = message.from_user.id
    save_response(user_id, materials_format=materials_format)

    if materials_format == "на бумаге":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="учебник"), KeyboardButton(text="рукописный конспект")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Что именно у вас на бумаге?", reply_markup=keyboard)
        await state.set_state(SurveyStates.paper_type)
    else:  # оцифрованные
        # Используем клавиатуру с множественным выбором?
        # Но aiogram не поддерживает множественный выбор в ReplyKeyboard без доп. логики.
        # Поэтому предложим выбрать ОДИН вариант или "несколько" → но проще — дать выбрать основной.
        # Или используем кнопки и разрешим несколько нажатий?
        # Для простоты — выбор одного типа (можно расширить позже).
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="учебники")],
                [KeyboardButton(text="вебинары")],
                [KeyboardButton(text="презентации")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Какой тип оцифрованных материалов у вас есть?", reply_markup=keyboard)
        await state.set_state(SurveyStates.digital_types)

@router.message(SurveyStates.materials_format)
async def invalid_materials_format(message: Message):
    await message.answer("Пожалуйста, выберите 'оцифрованные' или 'на бумаге'.")


# --- 4. Тип бумаги ---
@router.message(SurveyStates.paper_type, F.text.in_({"учебник", "рукописный конспект"}))
async def process_paper_type(message: Message, state: FSMContext):
    paper_type = message.text
    user_id = message.from_user.id
    save_response(user_id, paper_type=paper_type)

    if paper_type == "учебник":
        await message.answer("Укажите объём учебника в страницах (целое число):")
        await state.set_state(SurveyStates.textbook_pages)
    else:
        # Конспект → завершаем
        await _finish_survey(message, state)

@router.message(SurveyStates.paper_type)
async def invalid_paper_type(message: Message):
    await message.answer("Пожалуйста, выберите 'учебник' или 'рукописный конспект'.")


# --- 5. Объём учебника ---
@router.message(SurveyStates.textbook_pages)
async def process_textbook_pages(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите положительное целое число (например, 250):")
        return
    save_response(message.from_user.id, textbook_pages=int(message.text))
    await _finish_survey(message, state)


# --- 6. Тип оцифрованных материалов ---
@router.message(SurveyStates.digital_types, F.text.in_({"учебники", "вебинары", "презентации"}))
async def process_digital_types(message: Message, state: FSMContext):
    save_response(message.from_user.id, digital_types=message.text)
    await _finish_survey(message, state)

@router.message(SurveyStates.digital_types)
async def invalid_digital_types(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных типов.")


# --- Завершение анкеты ---
async def _finish_survey(message: Message, state: FSMContext):
    explanation = (
        "🧠 <b>О нашем ассистенте:</b>\n\n"
        "Речь идёт о человеке, который в день экзамена приедет к вам, "
        "привезёт необходимое оборудование (если нужно) и поможет спокойно сдать экзамен.\n\n"
        "Вы готовы встретить такого помощника?"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="нет возможности"), KeyboardButton(text="да, готов")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(explanation, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(SurveyStates.assistant_welcome)
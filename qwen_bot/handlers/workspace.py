from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

router = Router()


# --- 1. Место проведения: очно / онлайн ---
@router.message(SurveyStates.has_examples, F.text.in_({"да", "нет"}))
async def after_has_examples(message: Message, state: FSMContext):
    save_response(message.from_user.id, has_examples=message.text)

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


# --- 2. Место проведения: выбор ---
@router.message(SurveyStates.exam_location, F.text.in_({"очно", "онлайн"}))
async def process_exam_location(message: Message, state: FSMContext):
    location = message.text
    user_id = message.from_user.id
    save_response(user_id, exam_location=location)

    if location == "онлайн":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Десктоп"), KeyboardButton(text="Ноутбук")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Какое устройство вы будете использовать?", reply_markup=keyboard)
        await state.set_state(SurveyStates.device_type)
    else:
        # Очно — пропускаем все вопросы про устройство и прокторинг
        await _finish_or_continue(user_id, message, state)


@router.message(SurveyStates.exam_location)
async def invalid_exam_location(message: Message):
    await message.answer("Пожалуйста, выберите 'очно' или 'онлайн'.")


# --- 3. Тип устройства (онлайн) ---
@router.message(SurveyStates.device_type, F.text.in_({"Десктоп", "Ноутбук"}))
async def process_device_type(message: Message, state: FSMContext):
    device = message.text
    user_id = message.from_user.id
    save_response(user_id, device_type=device)

    if device == "Десктоп":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="да"), KeyboardButton(text="нет")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Есть ли у вас веб-камера?", reply_markup=keyboard)
        await state.set_state(SurveyStates.has_camera)
    else:
        # Ноутбук — камера обычно есть, но всё равно спросим про прокторинг
        await _ask_proctoring_type(message, state)


@router.message(SurveyStates.device_type)
async def invalid_device_type(message: Message):
    await message.answer("Пожалуйста, выберите 'Десктоп' или 'Ноутбук'.")


# --- 4. Наличие камеры (только для десктопа) ---
@router.message(SurveyStates.has_camera, F.text.in_({"да", "нет"}))
async def process_has_camera(message: Message, state: FSMContext):
    save_response(message.from_user.id, has_camera=message.text)
    await _ask_proctoring_type(message, state)


@router.message(SurveyStates.has_camera)
async def invalid_has_camera(message: Message):
    await message.answer("Пожалуйста, выберите 'да' или 'нет'.")


# --- Вспомогательная функция: запрос типа прокторинга ---
async def _ask_proctoring_type(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="человек"), KeyboardButton(text="робот")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Кто будет осуществлять прокторинг?", reply_markup=keyboard)
    await state.set_state(SurveyStates.proctoring_type)


# --- 5. Тип прокторинга ---
@router.message(SurveyStates.proctoring_type, F.text.in_({"человек", "робот"}))
async def process_proctoring_type(message: Message, state: FSMContext):
    proctoring_type = message.text
    user_id = message.from_user.id
    save_response(user_id, proctoring_type=proctoring_type)

    if proctoring_type == "робот":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Экзамус"), KeyboardButton(text="ПрокторЕду")],
                [KeyboardButton(text="Другой")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Выберите систему прокторинга:", reply_markup=keyboard)
        await state.set_state(SurveyStates.proctoring_system)
    else:
        # Человек — завершаем блок
        await _finish_or_continue(user_id, message, state)


@router.message(SurveyStates.proctoring_type)
async def invalid_proctoring_type(message: Message):
    await message.answer("Пожалуйста, выберите 'человек' или 'робот'.")


# --- 6. Система прокторинга (если робот) ---
@router.message(SurveyStates.proctoring_system, F.text.in_({"Экзамус", "ПрокторЕду"}))
async def process_known_proctoring(message: Message, state: FSMContext):
    save_response(message.from_user.id, proctoring_system=message.text)
    await _finish_or_continue(message.from_user.id, message, state)


@router.message(SurveyStates.proctoring_system, F.text == "Другой")
async def other_proctoring_system(message: Message, state: FSMContext):
    await message.answer("Укажите название системы прокторинга:")
    await state.set_state(SurveyStates.other_proctoring)


@router.message(SurveyStates.proctoring_system)
async def invalid_proctoring_system(message: Message):
    await message.answer("Пожалуйста, выберите систему из списка.")


# --- 7. Уточнение для "Другой" ---
@router.message(SurveyStates.other_proctoring)
async def process_other_proctoring(message: Message, state: FSMContext):
    other_name = message.text.strip()
    if len(other_name) < 2:
        await message.answer("Название слишком короткое. Попробуйте снова:")
        return
    save_response(message.from_user.id, proctoring_system="Другой", other_proctoring=other_name)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1"), KeyboardButton(text="2")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Сколько камер используется в системе?", reply_markup=keyboard)
    await state.set_state(SurveyStates.camera_count)


# --- 8. Количество камер ---
@router.message(SurveyStates.camera_count, F.text.in_({"1", "2"}))
async def process_camera_count(message: Message, state: FSMContext):
    save_response(message.from_user.id, camera_count=int(message.text))
    await _finish_or_continue(message.from_user.id, message, state)


@router.message(SurveyStates.camera_count)
async def invalid_camera_count(message: Message):
    await message.answer("Пожалуйста, выберите '1' или '2'.")


# --- Завершение анкеты ---
async def _finish_or_continue(user_id: int, message: Message, state: FSMContext):

    # Переход к блоку материалов
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="да"), KeyboardButton(text="нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("У вас есть материалы для подготовки к экзамену?", reply_markup=keyboard)
    await state.set_state(SurveyStates.materials_exist)

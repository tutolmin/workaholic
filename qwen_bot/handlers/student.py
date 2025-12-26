from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

router = Router()

# --- Старт опроса ---
@router.message(Command("survey"))
async def start_survey(message: Message, state: FSMContext):
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
    save_response(message.from_user.id, age_group=message.text)
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

# --- Город: выбор ---
@router.message(SurveyStates.city_choice, F.text == "Москва")
async def city_moscow(message: Message, state: FSMContext):
    save_response(message.from_user.id, city="Москва")
    await message.answer("Введите название экзамена (минимум 3 буквы):")
    await state.set_state(SurveyStates.exam_name)

@router.message(SurveyStates.city_choice, F.text == "Другой")
async def city_other(message: Message, state: FSMContext):
    await message.answer("Введите название города (минимум 3 буквы):")
    await state.set_state(SurveyStates.city_input)

@router.message(SurveyStates.city_choice)
async def invalid_city_choice(message: Message):
    await message.answer("Пожалуйста, выберите 'Москва' или 'Другой'.")

# --- Город: ввод ---
@router.message(SurveyStates.city_input)
async def process_city_input(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city.isalpha() or len(city) < 3:
        await message.answer("Название города должно содержать только буквы и быть не короче 3 символов.")
        return
    save_response(message.from_user.id, city=city)
    await message.answer("Введите название экзамена (минимум 3 буквы):")
    await state.set_state(SurveyStates.exam_name)
    
# Обработка кнопки "Начать анкету" из /start
@router.message(F.text == "📝 Начать анкету")
async def start_survey_via_button(message: Message, state: FSMContext):
    # Тот же код, что и в /survey
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
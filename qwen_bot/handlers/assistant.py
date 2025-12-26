from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

router = Router()

# --- Запуск блока "Ассистент" после materials ---
# Вызывается после завершения materials (см. _finish_survey в materials.py)

# --- Пояснение и первый вопрос ---
@router.message(SurveyStates.digital_types)  # последнее состояние materials
async def after_materials(message: Message, state: FSMContext):
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

# Обрабатываем и другие возможные выходы из materials (например, если нет материалов)
@router.message(SurveyStates.textbook_pages)
@router.message(SurveyStates.paper_type, F.text == "рукописный конспект")
@router.message(SurveyStates.materials_exist, F.text == "нет")
async def after_materials_short(message: Message, state: FSMContext):
    # Эти состояния тоже ведут к ассистенту
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


# --- Ответ на готовность ---
@router.message(SurveyStates.assistant_welcome, F.text.in_({"нет возможности", "да, готов"}))
async def process_assistant_welcome(message: Message, state: FSMContext):
    welcome = message.text
    user_id = message.from_user.id
    save_response(user_id, assistant_welcome=welcome)

    if welcome == "да, готов":
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="утро"), KeyboardButton(text="день"), KeyboardButton(text="вечер")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Укажите удобное время дня для приезда ассистента:", reply_markup=keyboard)
        await state.set_state(SurveyStates.assistant_time)
    else:
        # "нет возможности" → завершаем анкету
        await _finish_survey(message, state)

@router.message(SurveyStates.assistant_welcome)
async def invalid_assistant_welcome(message: Message):
    await message.answer("Пожалуйста, выберите один из предложенных вариантов.")


# --- Время дня ---
@router.message(SurveyStates.assistant_time, F.text.in_({"утро", "день", "вечер"}))
async def process_assistant_time(message: Message, state: FSMContext):
    save_response(message.from_user.id, assistant_time=message.text)
    await _finish_survey(message, state)

@router.message(SurveyStates.assistant_time)
async def invalid_assistant_time(message: Message):
    await message.answer("Пожалуйста, выберите: утро, день или вечер.")


# --- Финальное завершение анкеты ---
async def _finish_survey(message: Message, state: FSMContext):
    # Делаем переход к оплате:
    explanation = (
        "💳 <b>О стоимости услуги:</b>\n\n"
        "Надеемся, вы понимаете, что такая помощь — "
        "в подготовке, сопровождении во время экзамена и выезде ассистента — "
        "требует ресурсов и стоит денег.\n\n"
        "Вы в принципе готовы платить за такую поддержку?"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="да"), KeyboardButton(text="нет")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(explanation, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(SurveyStates.payment_agreement)
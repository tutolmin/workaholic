from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states import SurveyStates
from database import save_response

from typing import Optional

router = Router()

# --- Пояснение и первый вопрос о готовности платить ---
@router.message(SurveyStates.assistant_time)  # последнее состояние assistant
@router.message(SurveyStates.assistant_welcome, F.text == "нет возможности")
async def after_assistant(message: Message, state: FSMContext):
    explanation = (
        "💳 <b>О стоимости услуги:</b>\n\n"
        "Надеемся, вы понимаете, что такая помощь — "
        "в подготовке, сопровождении во время экзамена и выезде ассистента — "
        "требует ресурсов и стоит денег.\n\n"
        "Вы в принципе готовы платить за такую поддержку?"
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="да"), KeyboardButton(text="нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(explanation, parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(SurveyStates.payment_agreement)

# --- Согласие на оплату ---
@router.message(SurveyStates.payment_agreement, F.text.in_({"да", "нет"}))
async def process_payment_agreement(message: Message, state: FSMContext):
    agreement = message.text
    user_id = message.from_user.id
    save_response(user_id, payment_agreement=agreement)

    if agreement == "нет":
        await _finish_final(message, state)
    else:
        await message.answer("Укажите сумму (в рублях), которую вы готовы заплатить за выезд ассистента:")
        await state.set_state(SurveyStates.assistant_price)

@router.message(SurveyStates.payment_agreement)
async def invalid_payment_agreement(message: Message):
    await message.answer("Пожалуйста, выберите 'да' или 'нет'.")


# --- Вспомогательная функция валидации суммы ---
def parse_price(text: str) -> Optional[int]:
    text = text.strip().replace(" ", "").replace("₽", "")
    if text.isdigit():
        value = int(text)
        return value if value > 0 else None
    return None


# --- Цена за выезд ассистента ---
@router.message(SurveyStates.assistant_price)
async def process_assistant_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Пожалуйста, введите положительное целое число (например, 5000):")
        return
    save_response(message.from_user.id, assistant_price=price)
    await message.answer("Укажите сумму за сопровождение во время экзамена:")
    await state.set_state(SurveyStates.exam_support_price)


# --- Цена за сопровождение на экзамене ---
@router.message(SurveyStates.exam_support_price)
async def process_exam_support_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Пожалуйста, введите положительное целое число (например, 3000):")
        return
    save_response(message.from_user.id, exam_support_price=price)
    await message.answer("Укажите сумму за подготовку экзаменационных материалов:")
    await state.set_state(SurveyStates.materials_prep_price)


# --- Цена за подготовку материалов ---
@router.message(SurveyStates.materials_prep_price)
async def process_materials_prep_price(message: Message, state: FSMContext):
    price = parse_price(message.text)
    if price is None:
        await message.answer("Пожалуйста, введите положительное целое число (например, 2000):")
        return
    save_response(message.from_user.id, materials_prep_price=price)
    await _finish_final(message, state)


# --- Финальное завершение анкеты ---
async def _finish_final(message: Message, state: FSMContext):
    await message.answer(
        "✅ Анкета полностью завершена!\n\n"
        "Спасибо, что поделились своими ожиданиями и условиями. "
        "Эта информация поможет нам предложить вам максимально подходящий вариант поддержки.\n\n"
        "В ближайшее время с вами свяжется наш менеджер для уточнения деталей. 🌟"
    )
    await state.clear()
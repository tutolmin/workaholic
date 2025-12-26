from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import get_db_connection

router = Router()

def delete_incomplete_response(user_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM responses WHERE user_id = ?", (user_id,))
        conn.commit()

@router.message(Command("cancel"))
async def cancel_survey(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        # Даже если не в FSM — уберём клаву на всякий случай
        await message.answer("Вы не заполняете анкету.", reply_markup=ReplyKeyboardRemove())
        return

    user_id = message.from_user.id
#    delete_incomplete_response(user_id)
    await state.clear()
    await message.answer(
        "Анкета отменена.",
        reply_markup=ReplyKeyboardRemove()  # ← Это уберёт все кнопки!
    )
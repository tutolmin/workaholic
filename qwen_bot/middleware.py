# middleware.py
from aiogram import BaseMiddleware
from aiogram.types import Update, User
import logging

logger = logging.getLogger(__name__)


def get_user_from_update(update: Update) -> User | None:
    """Безопасно извлекает пользователя из любого типа Update."""
    if update.message:
        return update.message.from_user
    if update.callback_query:
        return update.callback_query.from_user
    if update.poll_answer:
        # poll_answer.user — но это не from_user, и может быть недоступен
        # В этом случае возвращаем None или обрабатываем отдельно
        return None
    if update.my_chat_member:
        return update.my_chat_member.from_user
    if update.chat_member:
        return update.chat_member.from_user
    # Добавьте другие типы по мере необходимости
    return None


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data):
        user = get_user_from_update(event)

        if user:
            user_info = f"[{user.id}] {user.full_name}"
            if user.username:
                user_info += f" (@{user.username})"
        else:
            user_info = "Unknown or system event"

        # Логируем в зависимости от типа события
        if event.message:
            text = event.message.text or event.message.caption or "[non-text message]"
            logger.info(f"{user_info} -> Message: {text}")
        elif event.callback_query:
            logger.info(f"{user_info} -> Callback: {event.callback_query.data}")
        elif event.poll_answer:
            logger.info(f"{user_info} -> Poll answer")
        elif event.my_chat_member:
            logger.info(f"{user_info} -> Chat member update")
        else:
            # Неизвестный тип — логируем кратко, чтобы не спамить
            logger.debug(f"{user_info} -> Other update type: {event.model_dump(exclude_defaults=True)}")

        return await handler(event, data)
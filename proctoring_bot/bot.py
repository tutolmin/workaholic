import logging
from telebot import TeleBot, types
from config_loader import ConfigLoader
from database import Database

# Настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "questions.json"
BOT_TOKEN = "8279054105:AAENxBgJaSGNqfLNQjF7mOOb3ZSEDz0SQDs"

# Инициализация
config_loader = ConfigLoader(CONFIG_FILE)
db = Database(config_loader=config_loader)
bot = TeleBot(BOT_TOKEN)

# Хранилище состояний
user_states = {}


class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_question_index = 0

    def get_current_question(self):
        if self.current_question_index < len(config_loader.questions):
            return config_loader.questions[self.current_question_index]
        return None

    def next_question(self):
        self.current_question_index += 1


# Команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user_info = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name
    }

    # Сбрасываем состояние
    user_states[user_id] = UserState(user_id)

    # Отправляем приветствие
    welcome_msg = config_loader.config.get('welcome_message', '👋 Привет!')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Начать опрос"))
    markup.add(types.KeyboardButton("📋 Мои ответы"))

    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)


# Начало опроса
@bot.message_handler(func=lambda msg: msg.text == "📝 Начать опрос")
def start_survey(message):
    user_id = message.from_user.id

    if user_id not in user_states:
        user_states[user_id] = UserState(user_id)

    send_current_question(message.chat.id, user_id)


# Отправка текущего вопроса
def send_current_question(chat_id, user_id):
    state = user_states[user_id]
    question = state.get_current_question()

    if not question:
        complete_survey(chat_id, user_id)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if question['type'] == 'buttons':
        for option in question['options']:
            markup.add(types.KeyboardButton(option))

    elif question['type'] == 'text_with_buttons' and 'quick_options' in question:
        for option in question['quick_options']:
            markup.add(types.KeyboardButton(option))

    markup.add(types.KeyboardButton("❌ Отменить"))

    bot.send_message(chat_id, question['text'], reply_markup=markup)


# Обработка ответов
@bot.message_handler(func=lambda msg: msg.from_user.id in user_states)
def handle_answer(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    question = state.get_current_question()

    if not question:
        return

    if message.text == "❌ Отменить":
        cancel_survey(message.chat.id, user_id)
        return

    user_info = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name
    }

    # Валидация
    if question['type'] == 'buttons':
        if message.text not in question['options']:
            bot.send_message(
                message.chat.id,
                f"Пожалуйста, выберите один из вариантов:"
            )
            return

    # Для города: если выбран "Другой", запрашиваем ввод
    if question['id'] == 'city' and question.get('quick_options'):
        if message.text == "Другой":
            bot.send_message(
                message.chat.id,
                "✏️ Напишите название вашего города:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            # Устанавливаем флаг ожидания
            if 'waiting_for_city' not in user_states[user_id].__dict__:
                user_states[user_id].__dict__['waiting_for_city'] = True
            return

        # Если ждем ввод города
        if user_states[user_id].__dict__.get('waiting_for_city'):
            answer = message.text
            user_states[user_id].__dict__['waiting_for_city'] = False
        else:
            answer = message.text
    else:
        answer = message.text

    # Сохраняем ответ
    db.save_answer(user_id, question['id'], answer, user_info)

    # Переходим к следующему вопросу
    state.next_question()

    # Отправляем следующий вопрос или завершаем
    if state.current_question_index < len(config_loader.questions):
        send_current_question(message.chat.id, user_id)
    else:
        complete_survey(message.chat.id, user_id)


# Обработчик ввода города
@bot.message_handler(func=lambda msg:
msg.from_user.id in user_states and
user_states[msg.from_user.id].__dict__.get('waiting_for_city'))
def handle_city_input(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    question = state.get_current_question()

    if message.text == "❌ Отменить":
        cancel_survey(message.chat.id, user_id)
        return

    user_info = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name
    }

    # Сохраняем город
    db.save_answer(user_id, question['id'], message.text, user_info)

    # Сбрасываем флаг
    user_states[user_id].__dict__['waiting_for_city'] = False

    # Переходим к следующему вопросу
    state.next_question()

    if state.current_question_index < len(config_loader.questions):
        send_current_question(message.chat.id, user_id)
    else:
        complete_survey(message.chat.id, user_id)


# Завершение опроса
def complete_survey(chat_id, user_id):
    completion_msg = config_loader.config.get('completion_message', '✅ Анкета заполнена!')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📋 Мои ответы"))
    markup.add(types.KeyboardButton("📝 Пройти заново"))

    bot.send_message(chat_id, completion_msg, reply_markup=markup)

    # Очищаем состояние
    if user_id in user_states:
        del user_states[user_id]


# Просмотр ответов
@bot.message_handler(func=lambda msg: msg.text == "📋 Мои ответы")
def show_answers(message):
    user_id = message.from_user.id
    responses = db.get_user_responses(user_id)

    if not responses:
        bot.send_message(message.chat.id, "У вас пока нет сохраненных ответов.")
        return

    # Формируем сообщение с ответами
    response_text = "📋 **Ваши ответы:**\n\n"

    for question in config_loader.questions:
        answer = responses.get(question['id'])
        if answer and answer not in ['', None]:
            response_text += f"**{question['text']}**\n→ {answer}\n\n"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Проверяем, заполнена ли анкета полностью
    if db.is_completed(user_id):
        markup.add(types.KeyboardButton("📝 Пройти заново"))
    else:
        markup.add(types.KeyboardButton("📝 Продолжить опрос"))

    markup.add(types.KeyboardButton("❌ Отменить"))

    bot.send_message(message.chat.id, response_text, reply_markup=markup, parse_mode='Markdown')


# Продолжить опрос
@bot.message_handler(func=lambda msg: msg.text == "📝 Продолжить опрос")
def continue_survey(message):
    user_id = message.from_user.id

    # Определяем, с какого вопроса продолжить
    responses = db.get_user_responses(user_id)
    current_index = 0

    for i, question in enumerate(config_loader.questions):
        answer = responses.get(question['id'])
        if not answer or answer == '':
            current_index = i
            break
    else:
        # Все вопросы заполнены
        complete_survey(message.chat.id, user_id)
        return

    # Устанавливаем состояние
    user_states[user_id] = UserState(user_id)
    user_states[user_id].current_question_index = current_index

    send_current_question(message.chat.id, user_id)


# Пройти заново
@bot.message_handler(func=lambda msg: msg.text == "📝 Пройти заново")
def restart_survey(message):
    user_id = message.from_user.id

    # Удаляем старые ответы
    db.delete_user_responses(user_id)

    # Очищаем состояние
    if user_id in user_states:
        del user_states[user_id]

    # Начинаем заново
    start_survey(message)


# Отмена
def cancel_survey(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Начать опрос"))
    markup.add(types.KeyboardButton("📋 Мои ответы"))

    bot.send_message(
        chat_id,
        "❌ Опрос отменен.",
        reply_markup=markup
    )


# Запуск бота
if __name__ == '__main__':
    logger.info(f"Бот запущен с {len(config_loader.questions)} вопросами")
    bot.infinity_polling()
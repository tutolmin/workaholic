import sqlite3
import logging
from datetime import datetime
from telebot import TeleBot, types

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен бота (замените на свой)
BOT_TOKEN = "8279054105:AAENxBgJaSGNqfLNQjF7mOOb3ZSEDz0SQDs"

# Инициализация бота
bot = TeleBot(BOT_TOKEN)

# Класс для работы с базой данных
class SurveyDatabase:
    def __init__(self, db_name="simple_survey.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                name TEXT,
                student_age_group TEXT,
                student_city TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    
    def save_response(self, user_id, username, first_name, field, value):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_responses WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(f'''
                UPDATE user_responses 
                SET {field} = ?, updated_at = ?
                WHERE user_id = ?
            ''', (value, datetime.now(), user_id))
        else:
            cursor.execute('''
                INSERT INTO user_responses 
                (user_id, username, first_name, name, student_age_group, student_city)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, '', '', ''))
            
            cursor.execute(f'''
                UPDATE user_responses 
                SET {field} = ?, updated_at = ?
                WHERE user_id = ?
            ''', (value, datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Сохранен ответ для user_id {user_id}: {field} = {value}")
    
    def get_user_response(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, student_age_group, student_city 
            FROM user_responses 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'name': result[0],
                'student_age_group': result[1],
                'student_city': result[2]
            }
        return None
    
    def is_completed(self, user_id):
        response = self.get_user_response(user_id)
        if response:
            return all(response.values())
        return False

# Инициализация базы данных
db = SurveyDatabase()

# Вопросы опросника
QUESTIONS = [
    {
        'id': 'name',
        'text': '📝 Как вас зовут?',
        'type': 'text'
    },
    {
        'id': 'student_age_group',
        'text': '🎂 Выберите вашу возрастную группу:',
        'type': 'buttons',
        'options': ['до 16 лет', '16-18 лет', '18+ лет']
    },
    {
        'id': 'student_city',
        'text': '🏙️ Из какого вы города?\n(Можете выбрать Москву или написать любой город)',
        'type': 'text_with_buttons'
    }
]

# Хранилище состояний пользователей
user_states = {}

# Команда /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Сбрасываем состояние пользователя
    user_states[user_id] = {'current_question': 0}
    
    # Проверяем, есть ли уже заполненная анкета
    if db.is_completed(user_id):
        show_results(message)
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_start = types.KeyboardButton("📝 Начать опрос")
    markup.add(item_start)
    
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {first_name}!\n\n"
        f"Я помогу заполнить простую анкету.\n"
        f"Всего 3 вопроса:\n"
        f"1. Ваше имя\n"
        f"2. Возрастная группа\n"
        f"3. Город\n\n"
        f"Нажмите кнопку ниже, чтобы начать ⬇️",
        reply_markup=markup
    )

# Начало опроса
@bot.message_handler(func=lambda message: message.text == "📝 Начать опрос")
def start_survey(message):
    user_id = message.from_user.id
    
    if db.is_completed(user_id):
        show_results(message)
        return
    
    user_states[user_id] = {'current_question': 0}
    send_question(message.chat.id, user_id)

# Отправка вопроса
def send_question(chat_id, user_id):
    state = user_states.get(user_id)
    
    if not state or state['current_question'] >= len(QUESTIONS):
        check_completion(chat_id, user_id)
        return
    
    question = QUESTIONS[state['current_question']]
    
    if question['type'] == 'buttons':
        # Кнопки для возраста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for option in question['options']:
            markup.add(types.KeyboardButton(option))
        markup.add(types.KeyboardButton("❌ Отменить"))
        
    elif question['type'] == 'text_with_buttons':
        # Кнопки для города + возможность ввода текста
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn_moscow = types.KeyboardButton("Москва")
        btn_other = types.KeyboardButton("Другой город")
        markup.add(btn_moscow, btn_other)
        markup.add(types.KeyboardButton("❌ Отменить"))
        
    else:  # обычный текст
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌ Отменить"))
    
    bot.send_message(
        chat_id,
        question['text'],
        reply_markup=markup
    )

# Обработка ответов
@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_answer(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    state = user_states[user_id]
    
    if message.text == "❌ Отменить":
        cancel_survey(message.chat.id, user_id)
        return
    
    current_q_index = state['current_question']
    question = QUESTIONS[current_q_index]
    
    # ВАЖНОЕ ИЗМЕНЕНИЕ: Для города принимаем ЛЮБОЙ текст
    if question['id'] == 'student_city':
        # Принимаем любой текст как название города
        field_value = message.text
        # Но если выбрана кнопка "Другой город", запрашиваем уточнение
        if message.text == "Другой город":
            bot.send_message(
                message.chat.id,
                "✏️ Напишите название вашего города:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            # Устанавливаем флаг ожидания города
            user_states[user_id]['waiting_for_student_city'] = True
            return
        
        # Если мы ждем ввод города после нажатия "Другой город"
        elif user_states[user_id].get('waiting_for_student_city'):
            field_value = message.text
            user_states[user_id]['waiting_for_student_city'] = False
    
    # Для возраста проверяем, что выбран правильный вариант
    elif question['id'] == 'student_age_group':
        if message.text not in question['options']:
            bot.send_message(
                message.chat.id,
                f"Пожалуйста, выберите один из вариантов:\n" +
                "\n".join([f"• {opt}" for opt in question['options']])
            )
            return
        field_value = message.text
    
    # Для имени принимаем любой текст
    else:
        field_value = message.text
    
    # Сохраняем ответ в БД
    db.save_response(user_id, username, first_name, question['id'], field_value)
    
    # Переходим к следующему вопросу
    state['current_question'] += 1
    
    # Проверяем заполненность
    if db.is_completed(user_id):
        show_results(message)
        if user_id in user_states:
            del user_states[user_id]
    else:
        send_question(message.chat.id, user_id)

# Проверка заполненности анкеты
def check_completion(chat_id, user_id):
    if db.is_completed(user_id):
        response = db.get_user_response(user_id)
        
        summary = "✅ **Анкета заполнена!**\n\n"
        summary += "**Ваши данные:**\n"
        summary += f"👤 Имя: {response['name']}\n"
        summary += f"🎂 Возраст: {response['student_age_group']}\n"
        summary += f"🏙️ Город: {response['student_city']}\n\n"
        summary += "Спасибо за участие!"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("📝 Пройти заново"))
        
        bot.send_message(chat_id, summary, reply_markup=markup, parse_mode='Markdown')
        
        if user_id in user_states:
            del user_states[user_id]
    else:
        send_question(chat_id, user_id)

# Показ результатов
def show_results(message):
    user_id = message.from_user.id
    response = db.get_user_response(user_id)
    
    if not response:
        start_survey(message)
        return
    
    summary = "📋 **Ваша анкета:**\n\n"
    summary += f"👤 Имя: {response['name']}\n"
    summary += f"🎂 Возраст: {response['student_age_group']}\n"
    summary += f"🏙️ Город: {response['student_city']}\n\n"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Пройти заново"))
    
    bot.send_message(
        message.chat.id,
        summary + "Чтобы изменить данные, нажмите кнопку ниже ⬇️",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Прохождение заново
@bot.message_handler(func=lambda message: message.text == "📝 Пройти заново")
def restart_survey(message):
    user_id = message.from_user.id
    
    # Сбрасываем данные в БД
    conn = sqlite3.connect(db.db_name)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_responses WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    # Начинаем опрос заново
    start_survey(message)

# Отмена опроса
def cancel_survey(chat_id, user_id):
    if user_id in user_states:
        del user_states[user_id]
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📝 Начать опрос"))
    
    bot.send_message(
        chat_id,
        "❌ Опрос отменен. Ваши частично заполненные данные сохранены.\n"
        "Вы можете продолжить позже, нажав 'Начать опрос'.",
        reply_markup=markup
    )

# Команда /view - просмотр своей анкеты
@bot.message_handler(commands=['view'])
def view_my_data(message):
    user_id = message.from_user.id
    response = db.get_user_response(user_id)
    
    if not response or not any(response.values()):
        bot.send_message(
            message.chat.id,
            "📭 У вас нет сохраненной анкеты.\n"
            "Начните опрос командой /start"
        )
        return
    
    summary = "📋 **Ваша анкета:**\n\n"
    
    if response['name']:
        summary += f"👤 Имя: {response['name']}\n"
    else:
        summary += "👤 Имя: ❌ не указано\n"
    
    if response['student_age_group']:
        summary += f"🎂 Возраст: {response['student_age_group']}\n"
    else:
        summary += "🎂 Возраст: ❌ не указан\n"
    
    if response['student_city']:
        summary += f"🏙️ Город: {response['student_city']}\n"
    else:
        summary += "🏙️ Город: ❌ не указан\n"
    
    filled_fields = sum(1 for field in response.values() if field)
    total_fields = len(response)
    progress = filled_fields / total_fields * 100
    
    summary += f"\n📊 Заполнено: {filled_fields}/{total_fields} ({progress:.0f}%)"
    
    if filled_fields < total_fields:
        summary += "\n\nЧтобы продолжить заполнение, нажмите /continue"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if filled_fields < total_fields:
        markup.add(types.KeyboardButton("📝 Продолжить заполнение"))
    else:
        markup.add(types.KeyboardButton("📝 Пройти заново"))
    
    bot.send_message(
        message.chat.id,
        summary,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Команда /continue - продолжить заполнение
@bot.message_handler(commands=['continue'])
@bot.message_handler(func=lambda message: message.text == "📝 Продолжить заполнение")
def continue_survey(message):
    user_id = message.from_user.id
    
    if db.is_completed(user_id):
        show_results(message)
        return
    
    response = db.get_user_response(user_id)
    
    current_question = 0
    if response['name']:
        current_question += 1
    if response['student_age_group']:
        current_question += 1
    if response['student_city']:
        current_question += 1
    
    user_states[user_id] = {'current_question': current_question}
    send_question(message.chat.id, user_id)

# Помощь
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📋 **Помощь по боту:**

/start - Начать опрос
/view - Посмотреть свою анкету
/continue - Продолжить заполнение
/help - Эта справка

**Как это работает:**
1. Нажимаете "Начать опрос"
2. Отвечаете на 3 простых вопроса:
   • Имя (любой текст)
   • Возрастная группа (выбрать из кнопок)
   • Город (можно выбрать Москву, Другой город или написать любой город)
3. Ваши ответы сохраняются после каждого вопроса
4. Можете прерваться и продолжить позже
5. В любой момент можете посмотреть свои данные

❌ **Отмена:** Нажмите кнопку "Отменить" в любой момент
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Обработчик для текста, когда ждем ввод города
@bot.message_handler(func=lambda message: 
                     message.from_user.id in user_states and 
                     user_states[message.from_user.id].get('waiting_for_student_city'))
def handle_student_city_input(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    if message.text == "❌ Отменить":
        cancel_survey(message.chat.id, user_id)
        return
    
    # Сохраняем введенный город
    db.save_response(user_id, username, first_name, 'student_city', message.text)
    
    # Убираем флаг ожидания
    user_states[user_id]['waiting_for_student_city'] = False
    user_states[user_id]['current_question'] += 1
    
    # Проверяем заполненность
    if db.is_completed(user_id):
        show_results(message)
        if user_id in user_states:
            del user_states[user_id]
    else:
        send_question(message.chat.id, user_id)

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот-опросник запущен...")
    bot.infinity_polling()


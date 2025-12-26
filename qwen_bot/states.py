from aiogram.fsm.state import State, StatesGroup

class SurveyStates(StatesGroup):
    # Блок 1: Возраст и город
    age = State()
    city_choice = State()
    city_input = State()

    # Блок 2: Основные параметры экзамена
    exam_name = State()
    exam_type = State()
    test_subtype = State()
    task_count = State()
    time_choice = State()
    time_custom = State()
    attempts = State()

    # Блок 3: Дополнительные параметры
    passing_score = State()
    required_result = State()
    exam_date = State()
    importance = State()
    has_examples = State()

    # Блок: Рабочее место и прокторинг
    exam_location = State()        # очно / онлайн
    device_type = State()          # десктоп / ноутбук
    has_camera = State()           # есть ли камера (только для десктопа)
    proctoring_type = State()      # человек / робот
    proctoring_system = State()    # Экзамус / ПрокторЕду / Другой
    other_proctoring = State()     # уточнение для "Другой"
    camera_count = State()         # 1 или 2 камеры (если Другой)

    # Блок: Материалы (новый)
    materials_exist = State()        # есть / нет
    materials_format = State()       # оцифрованные / на бумаге
    paper_type = State()             # учебник / конспект
    textbook_pages = State()         # объём учебника (если учебник)
    digital_types = State()          # выбор типов для оцифрованных

    # Блок: Ассистент (новый)
    assistant_welcome = State()    # готовы ли принять ассистента?
    assistant_time = State()       # удобное время (если "готов")

    # Блок: Оплата (новый)
    payment_agreement = State()        # готовы ли платить?
    assistant_price = State()          # цена за выезд ассистента
    exam_support_price = State()       # цена за сопровождение на экзамене
    materials_prep_price = State()     # цена за подготовку материалов
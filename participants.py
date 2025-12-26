from telethon.sync import TelegramClient
import csv
import json

# Ваши учетные данные
api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'

# ID группы (можно использовать как числовой ID, так и юзернейм)
group_id = 1002193712593  # Замените на ID вашей группы или используйте '@username'

# Имена файлов для экспорта
csv_filename = 'group_contacts.csv'
json_filename = 'group_contacts.json'

with TelegramClient('anon', api_id, api_hash) as client:
    try:
        # Получаем информацию о группе
        group = client.get_entity(group_id)
        print(f"Работаем с группой: {group.title}")
        
        # Получаем всех участников группы
        print("Получаем участников группы...")
        participants = client.get_participants(group)
        
        print(f"Найдено участников: {len(participants)}")
        
        # Подготовка данных для экспорта
        contacts_data = []
        
        for participant in participants:
            # Извлекаем информацию об участнике
            user_id = participant.id
            first_name = participant.first_name or ""
            last_name = participant.last_name or ""
            username = participant.username or ""
            phone = participant.phone or ""
            
            # Полное имя
            full_name = f"{first_name} {last_name}".strip()
            
            # Добавляем в список
            contacts_data.append({
                'id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'full_name': full_name,
                'username': username,
                'phone': phone
            })
            
            # Выводим информацию в консоль
            print(f"ID: {user_id}, Имя: {full_name}, @{username}, Телефон: {phone}")
        
        # Экспорт в CSV
        print(f"\nЭкспортируем данные в CSV файл: {csv_filename}")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'first_name', 'last_name', 'full_name', 'username', 'phone']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(contacts_data)
        
        # Экспорт в JSON
        print(f"Экспортируем данные в JSON файл: {json_filename}")
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(contacts_data, jsonfile, ensure_ascii=False, indent=2)
        
        print(f"\nЭкспорт завершен!")
        print(f"Всего экспортировано: {len(contacts_data)} контактов")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        print("Возможные причины:")
        print("1. Неверный ID группы")
        print("2. Отсутствие прав администратора для просмотра участников")
        print("3. Проблемы с подключением к Telegram API")


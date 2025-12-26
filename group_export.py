# Дополнительный скрипт с расширенными функциями
from telethon.sync import TelegramClient
import csv
import json
from datetime import datetime

api_id = 25315069
api_hash = '419b7cd9f055a855ffd2f06948ab882e'
group_id = 1002193712593  # Или '@username'

def export_contacts():
    with TelegramClient('anon', api_id, api_hash) as client:
        try:
            # Получаем группу
            group = client.get_entity(group_id)
            print(f"Группа: {group.title}")
            
            # Получаем участников
            participants = client.get_participants(group, aggressive=True)
            
            # Подготавливаем данные
            contacts = []
            for user in participants:
                contact = {
                    'id': user.id,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'username': user.username or '',
                    'phone': user.phone or '',
                    'is_bot': user.bot,
                    'is_verified': user.verified,
                    'is_scam': user.scam,
                    'is_premium': user.premium if hasattr(user, 'premium') else False
                }
                contacts.append(contact)
            
            # Создаем timestamp для имен файлов
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Экспорт в несколько форматов
            export_formats(contacts, group.title, timestamp)
            
            return contacts
            
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

def export_formats(contacts, group_name, timestamp):
    # CSV экспорт
    csv_file = f'{group_name}_contacts_{timestamp}.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=contacts[0].keys())
        writer.writeheader()
        writer.writerows(contacts)
    
    # JSON экспорт
    json_file = f'{group_name}_contacts_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    
    # Текстовый экспорт
    txt_file = f'{group_name}_contacts_{timestamp}.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        for contact in contacts:
            f.write(f"ID: {contact['id']}\n")
            f.write(f"Имя: {contact['first_name']} {contact['last_name']}\n")
            f.write(f"Username: @{contact['username']}\n")
            f.write(f"Телефон: {contact['phone']}\n")
            f.write("-" * 40 + "\n")
    
    print(f"\nФайлы сохранены:")
    print(f"CSV: {csv_file}")
    print(f"JSON: {json_file}")
    print(f"TXT: {txt_file}")

if __name__ == "__main__":
    contacts = export_contacts()
    print(f"\nВсего обработано: {len(contacts)} контактов")

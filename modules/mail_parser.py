# -*- coding: utf-8 -*-
"""
Модуль получения и фильтрации писем.
"""

import ssl
import os
import socket
import imaplib
import email
import re
import json
import datetime
import yaml
from email.header import decode_header

def decode_str(s):
    """Универсальная функция декодирования строк"""
    if not s:
        return ''
    parts = decode_header(s)
    result = ''
    for text, encoding in parts:
        if isinstance(text, bytes):
            result += text.decode(encoding or 'utf-8', errors='ignore')
        else:
            result += text
    return result

def load_mail_settings(configs):
    """Настройки подключения из конфигов"""
    return configs.get('mail_settings.yaml', {})

def get_next_folder_number(base_path):
    """Получение номера следующей папки"""
    max_num = 0
    if os.path.exists(base_path):
        for name in os.listdir(base_path):
            match = re.match(r"(\d+)\(\d{2}.\d{2}.\d{4}\)", name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    return max_num + 1

def test_mail_connection(mail_cfg):
    """Тестирование подключения к почте"""
    
    # Параметры подключения
    server = mail_cfg.get('host', 'imap.gmail.com')
    username = mail_cfg.get('username', '')
    password = mail_cfg.get('password', '')
    port = mail_cfg.get('port', 993)
    
    # Проверяем доступность сервера
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server, port))
        sock.close()
        
        if result == 0:
            ...
        else:
            port = 143
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result == 0:
                ...
            else:
                return False, None
    except Exception as e:
        ...
    
    connection = None
    
    try:
        # Шаг 1: Создание SSL контекста
        context = ssl.create_default_context()
        # Отключаем проверку сертификата для локальных IP
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Шаг 2: Подключение к серверу
        try:
            # Пробуем SSL подключение
            connection = imaplib.IMAP4_SSL(server, port, ssl_context=context)
        except ssl.SSLError as ssl_error:
            try:
                # Пробуем обычное подключение на порту 143
                connection = imaplib.IMAP4(server, 143)
                port = 143
            except Exception as e:
                raise
        
        # Шаг 3: Получение возможностей сервера
        capabilities = connection.capabilities
        
        # Шаг 4: Авторизация
        connection.login(username, password)
        
        # Шаг 5: Получение списка папок
        _, folders = connection.list()
        folder_names = []
        for folder in folders:
            if b'"/"' in folder:
                folder_name = folder.decode().split('"')[-2]
                folder_names.append(folder_name)
        
        
        return True, connection
        
    except imaplib.IMAP4.error as e:
        return False, None
        
    except ssl.SSLError as e:
        return False, None
        
    except ConnectionRefusedError:
        return False, None
        
    except Exception as e:
        return False, None

def process_incoming_mail(configs):   
    mail_cfg = load_mail_settings(configs)
    imap_host = mail_cfg.get('host', 'imap.gmail.com')
    imap_user = mail_cfg.get('username', '')
    imap_pass = mail_cfg.get('password', '')
    mailbox = mail_cfg.get('mailbox', 'INBOX')
    save_dir = mail_cfg.get('save_dir', 'incoming')
    allowed_exts = set(mail_cfg.get('allowed_extensions', ['.xlsx', '.xls', '.zip', '.rar', '.pdf']))
    sender_filter = mail_cfg.get('sender_filter', [])
    subject_filter = mail_cfg.get('subject_filter', [])
    
    # Создаем директорию для сохранения
    os.makedirs(save_dir, exist_ok=True)
    
    # Тестируем подключение
    success, connection = test_mail_connection(mail_cfg)
    
    if not success:
        print("❌ Не удалось подключиться к почте")
        return
    
    try:
        # Выбираем папку
        connection.select(mailbox)
        print(f"папка {mailbox} выбрана")
        
        # Поиск писем (только новые/непрочитанные)
        status, messages = connection.search(None, 'SEEN')
        if status != 'OK':
            return
        
        message_list = messages[0].split()
        total_unread = len(message_list)
        print(f"непрочитанных писем: {total_unread}")
        
        if total_unread == 0:
            # return
            pass
        
        processed_count = 0
        saved_attachments = 0
        
        for i, num in enumerate(message_list, 1):
            print(f"\nобрабатываем письмо {i}/{total_unread}...")
            
            try:
                # Получаем письмо
                res, msg_data = connection.fetch(num, '(RFC822)')
                if res != 'OK':
                    print(f"⚠️ Не удалось загрузить письмо {num}")
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                from_addr = decode_str(msg.get('From', ''))
                subject = decode_str(msg.get('Subject', ''))
                date = decode_str(msg.get('Date', ''))
    
                
                # Фильтрация по отправителю и теме
                if sender_filter and not any(s in from_addr for s in sender_filter):
                    print(f"отправитель не в фильтре")
                    print(from_addr)
                    continue
                if subject_filter and not any(s in subject for s in subject_filter):
                    print(f"тема не в фильтре")
                    continue
                
                print("письмо прошло фильтрацию")
                
                # Формируем уникальную папку для письма
                date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_subject = ''.join(c for c in subject if c.isalnum() or c in (' ', '-', '_'))[:60]
                msg_dir = os.path.join(save_dir, f"{date_str}_{safe_subject}".strip())
                os.makedirs(msg_dir, exist_ok=True)
                print(f"📁 Создана папка: {msg_dir}")
                
                # Сохраняем вложения
                print("📎 Ищем вложения...")
                attach_count = 0
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    
                    filename = decode_str(part.get_filename())
                    if not filename:
                        continue
                    
                    ext = os.path.splitext(filename)[-1].lower()
                    if ext not in allowed_exts:
                        print(f"⏭️ Пропускаем {filename} - расширение {ext} не разрешено")
                        continue
                    
                    filepath = os.path.join(msg_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    attach_count += 1
                    print(f"💾 Сохранено: {filename}")
                
                if attach_count > 0:
                    print(f"✅ Сохранено вложений: {attach_count}")
                    saved_attachments += attach_count
                else:
                    print("ℹ️ Вложений не найдено")
                
                processed_count += 1
                print(f"✅ Письмо {i} обработано успешно")
                
            except Exception as e:
                print(f"❌ Ошибка при обработке письма {num}: {e}")
                continue
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📊 ИТОГИ ОБРАБОТКИ")
        print("=" * 60)
        print(f"📧 Всего непрочитанных писем: {total_unread}")
        print(f"✅ Успешно обработано: {processed_count}")
        print(f"💾 Сохранено вложений: {saved_attachments}")
        print(f"📁 Директория: {save_dir}")
        print("=" * 60)
        
        if processed_count > 0:
            print("🎉 Обработка почты завершена успешно!")
        else:
            print("ℹ️ Новых писем для обработки не найдено")
        
    except Exception as ex:
        print(f"❌ Ошибка обработки писем: {ex}")
        print("💡 Проверьте:")
        print("   - Доступность сервера")
        print("   - Правильность настроек")
        print("   - Права доступа к директории")
        
    finally:
        # Отключение от сервера
        if connection:
            try:
                connection.logout()
                print("🔌 Отключились от сервера")
            except:
                pass

def main():
    """Главная функция"""
    print("🧪 ПАРСЕР ПОЧТЫ")
    print("=" * 60)
    
    # Здесь можно загрузить конфиги
    configs = {
        'mail_settings.yaml': {
            'host': '192.168.180.13',
            'username': 'monakhov@storm-security.ru',
            'password': '8E1j?d$g',
            'port': 993,
            'mailbox': 'INBOX',
            'save_dir': 'incoming',
            'allowed_extensions': ['.xlsx', '.xls', '.zip', '.rar', '.pdf'],
            'sender_filter': [],
            'subject_filter': []
        }
    }
    
    process_incoming_mail(configs)

if __name__ == "__main__":
    main() 
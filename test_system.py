#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки системы автоматизации.
"""

import os
import sys
import json
import yaml
from datetime import datetime

def test_configs():
    """Тестирование загрузки конфигурации"""
    print("=== Тестирование конфигурации ===")
    
    # Проверяем наличие конфигурационных файлов
    config_files = [
        'config/input_fields.yaml',
        'config/required_fields.yaml',
        'config/enrichment_fields.yaml',
        'config/validators.yaml',
        'config/ftp_settings.yaml',
        'config/mail_settings.yaml',
        'config/paths.json',
        'config/formats.csv',
        'config/creditors_to_process.csv'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} - НЕ НАЙДЕН")
    
    # Тестируем загрузку YAML
    try:
        with open('config/input_fields.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(f"✅ YAML загружен: {len(data.get('input_fields', []))} полей")
    except Exception as e:
        print(f"❌ Ошибка загрузки YAML: {e}")
    
    # Тестируем загрузку JSON
    try:
        with open('config/paths.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ JSON загружен: {len(data)} кредиторов")
    except Exception as e:
        print(f"❌ Ошибка загрузки JSON: {e}")

def test_modules():
    """Тестирование импорта модулей"""
    print("\n=== Тестирование модулей ===")
    
    modules = [
        'modules.state_manager',
        'modules.config',
        'modules.mail_parser',
        'modules.archive_handler',
        'modules.excel_processor',
        'modules.validator',
        'modules.filewalker',
        'modules.parser',
        'modules.exporter',
        'modules.aggregate_exports',
        'modules.ftp_client',
        'modules.telegram_notifier'
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")

def test_directories():
    """Тестирование структуры директорий"""
    print("\n=== Тестирование директорий ===")
    
    directories = [
        'modules',
        'config',
        'logs',
        'data',
        'data/in',
        'data/out',
        'data/temp',
        'exports'
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - НЕ СУЩЕСТВУЕТ")

def test_dependencies():
    """Тестирование зависимостей"""
    print("\n=== Тестирование зависимостей ===")
    
    dependencies = [
        'pandas',
        'openpyxl',
        'yaml',
        'json',
        'logging',
        'os',
        'sys',
        'datetime'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except Exception as e:
            print(f"❌ {dep}: {e}")

def test_logging():
    """Тестирование логирования"""
    print("\n=== Тестирование логирования ===")
    
    try:
        from modules.state_manager import log_event, init_journals
        init_journals()
        log_event(stage="test", status="ok", message="Тестовое сообщение")
        print("✅ Логирование работает")
    except Exception as e:
        print(f"❌ Ошибка логирования: {e}")

def create_test_data():
    """Создание тестовых данных"""
    print("\n=== Создание тестовых данных ===")
    
    # Создаем тестовый JSON
    test_data = [
        {
            "number_ip": "12345678901",
            "fio": "Иванов Иван Иванович",
            "date": "01.01.2024",
            "creditor": "VALB",
            "file": "test_file.pdf"
        },
        {
            "number_ip": "98765432109",
            "fio": "Петров Петр Петрович", 
            "date": "02.01.2024",
            "creditor": "OZON",
            "file": "test_file2.pdf"
        }
    ]
    
    try:
        os.makedirs('exports', exist_ok=True)
        with open('exports/test_export.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print("✅ Тестовые данные созданы")
    except Exception as e:
        print(f"❌ Ошибка создания тестовых данных: {e}")

def main():
    """Основная функция тестирования"""
    print("Тестирование системы автоматизации обработки реестров")
    print("=" * 60)
    
    test_configs()
    test_modules()
    test_directories()
    test_dependencies()
    test_logging()
    create_test_data()
    
    print("\n" + "=" * 60)
    print("Тестирование завершено!")
    print("\nДля запуска системы выполните: python main.py")

if __name__ == "__main__":
    main() 
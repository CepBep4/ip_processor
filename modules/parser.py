# -*- coding: utf-8 -*-
"""
Модуль парсинга файлов.
"""

import os
import re
from .state_manager import log_event, log_error

def extract_text(file_path, ext):
    """Извлекает текст из файла по расширению"""
    if ext == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    if ext in ("xlsx", "xls"):
        return ""
    if ext == "pdf":
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            return text
        except Exception as ex:
            return ""
    return ""

def extract_fields_from_text(text, configs):
    """Извлекает поля с помощью регулярных выражений"""
    result = {}
    
    # Пример извлечения полей
    validators = configs.get('validators.yaml', {})
    
    # Дата
    date_regex = validators.get('date', {}).get('regex', r'\b\d{2}\.\d{2}\.\d{4}\b')
    date_match = re.search(date_regex, text)
    result['date'] = date_match.group(0) if date_match else ""

    # Номер договора
    number_regex = validators.get('number_ip', {}).get('regex', r'\b\d{8,13}\b')
    number_match = re.search(number_regex, text)
    result['number_ip'] = number_match.group(0) if number_match else ""

    # ФИО
    fio_regex = validators.get('fio', {}).get('regex', r'[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+')
    fio_match = re.search(fio_regex, text)
    result['fio'] = fio_match.group(0) if fio_match else ""

    return result

def parse_file(file_info, configs):
    """Парсинг одного файла"""
    file_path = file_info['file']
    creditor = file_info['creditor']
    ext = file_info['ext']

    try:
        if not os.path.exists(file_path):
            log_error(stage="parser", status="error", file=file_path, error_msg="File not found")
            return None

        text = extract_text(file_path, ext)
        if not text:
            log_error(stage="parser", status="error", file=file_path, error_msg="Empty text")
            return None

        doc_data = extract_fields_from_text(text, configs)
        doc_data['file'] = file_path
        doc_data['creditor'] = creditor

        log_event(stage="parser", status="ok", file=file_path, creditor=creditor, result="parsed")
        return doc_data

    except Exception as ex:
        log_error(stage="parser", status="error", file=file_path, error_msg=str(ex))
        return None

def process_files(files_to_process, configs):
    """Обработка списка файлов"""
    parsed = []
    for file_info in files_to_process:
        doc_data = parse_file(file_info, configs)
        if doc_data:
            parsed.append(doc_data)
    return parsed 
# -*- coding: utf-8 -*-
"""
Централизованное логирование и контроль статусов системы.
"""

import os
import json
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def _write_log(filename, entry):
    """Универсальная функция для записи лога"""
    path = os.path.join(LOG_DIR, filename)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

def log_event(**kwargs):
    """Логирует любое событие процесса: этап, статус, путь, комментарий"""
    entry = dict(datetime=str(datetime.now()), **kwargs)
    _write_log("process_log.json", entry)

def log_error(**kwargs):
    """Логирует все ошибки с деталями: этап, описание ошибки, файл и др."""
    entry = dict(datetime=str(datetime.now()), **kwargs)
    _write_log("error_log.json", entry)

def log_duplicate(file, contract_no, date):
    """Фиксирует каждый случай дублирования (по номеру договора и дате)"""
    entry = {
        "datetime": str(datetime.now()),
        "file": file,
        "contract_no": contract_no,
        "date": date,
        "event": "duplicate"
    }
    _write_log("duplicates_log.json", entry)

def log_not_processed(file, reason):
    """Фиксирует любые неразобранные или невалидные файлы с причиной"""
    entry = {
        "datetime": str(datetime.now()),
        "file": file,
        "reason": reason,
        "event": "not_processed"
    }
    _write_log("not_processed.json", entry)

def check_pause_flag():
    """Проверяет наличие pause.flag для экстренной остановки процесса"""
    return os.path.exists(os.path.join(LOG_DIR, "pause.flag"))

def init_journals():
    """Создаёт пустые журналы при первом запуске (если не существуют)"""
    for name in ["process_log.json", "error_log.json", "duplicates_log.json", "not_processed.json"]:
        path = os.path.join(LOG_DIR, name)
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                pass

def close_journals():
    """Заглушка: если нужно что-то сделать при завершении (архив, экспорт)"""
    pass 
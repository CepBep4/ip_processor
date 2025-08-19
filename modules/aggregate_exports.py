# -*- coding: utf-8 -*-
"""
Модуль агрегации экспортов.
"""

import os
import json
from datetime import datetime
from .state_manager import log_event

EXPORTS_DIR = "exports"
DATE_FMT = "%Y%m%d"

def get_files_for_date(date_str):
    """Находит все JSON-файлы с выгрузками за указанную дату"""
    files = []
    if os.path.exists(EXPORTS_DIR):
        for fname in os.listdir(EXPORTS_DIR):
            if fname.endswith('.json') and date_str in fname:
                files.append(os.path.join(EXPORTS_DIR, fname))
    return files

def aggregate_jsons(date_str):
    """Агрегирует все выгрузки за сутки"""
    files = get_files_for_date(date_str)
    seen_keys = set()
    aggregated = []
    
    for fpath in files:
        try:
            with open(fpath, encoding='utf-8') as f:
                items = json.load(f)
            for doc in items:
                # Используем кортеж (номер, дата) как ключ для уникальности
                key = (doc.get('number_ip'), doc.get('date'))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                aggregated.append(doc)
        except Exception as ex:
            log_event(stage="aggregate", status="error", file=fpath, error=str(ex))
            continue
    
    return aggregated

def save_aggregate(aggregated, date_str):
    """Сохраняет итоговый агрегированный файл за сутки"""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    out_name = f"IP_ARXIVE_{date_str}.json"
    out_path = os.path.join(EXPORTS_DIR, out_name)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(aggregated, f, ensure_ascii=False, indent=2)
    
    log_event(stage="aggregate", status="ok", file=out_path, count=len(aggregated))
    return out_path 
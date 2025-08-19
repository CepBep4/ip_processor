# -*- coding: utf-8 -*-
"""
Модуль экспорта данных в JSON.
"""

import os
import json
from datetime import datetime
from .state_manager import log_event

def export_to_json(ai_results, configs):
    """Экспорт результатов в JSON"""
    if not ai_results:
        log_event(stage="exporter", status="warning", message="Нет данных для экспорта")
        return None
    
    # Создаем папку для экспорта
    os.makedirs('exports', exist_ok=True)
    
    # Формируем имя файла
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_path = f"exports/export_{date_str}.json"
    
    # Сохраняем данные
    with open(export_path, 'w', encoding='utf-8') as f:
        json.dump(ai_results, f, ensure_ascii=False, indent=2)
    
    log_event(stage="exporter", status="ok", file=export_path, count=len(ai_results))
    return export_path 
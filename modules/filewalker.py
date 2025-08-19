# -*- coding: utf-8 -*-
"""
Модуль сбора файлов для обработки.
"""

import os
import json
import pandas as pd
from .state_manager import log_event

def load_creditor_dirs(configs):
    """Загружает список папок для обхода по каждому кредитору"""
    creditor_dirs = []
    df = configs.get('creditors_to_process.csv')
    if df is not None:
        for idx, row in df.iterrows():
            if str(row.get('status', '')).strip().lower() == 'к обработке':
                creditor_dirs.append({
                    'creditor': row['creditor'],
                    'path': row['link']
                })
    return creditor_dirs

def load_processed_files(log_path='logs/process_log.json'):
    """Считывает все уже обработанные файлы"""
    processed = set()
    if not os.path.exists(log_path):
        return processed
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get('status') == 'ok':
                    processed.add(entry.get('file'))
            except Exception:
                continue
    return processed

def collect_files(configs):
    """Собирает файлы для обработки"""
    files_for_processing = []
    allowed_exts = set()
    
    # Получаем разрешенные расширения
    formats_df = configs.get('formats.csv')
    if formats_df is not None:
        allowed_exts = set(formats_df['extension'].str.lower())
    else:
        allowed_exts = {'.xlsx', '.xls', '.pdf', '.docx', '.jpg', '.jpeg', '.png'}
    
    processed_files = load_processed_files()
    creditor_dirs = load_creditor_dirs(configs)

    # Проходим по всем кредиторам и их папкам
    for cinfo in creditor_dirs:
        base_dir = cinfo['path']
        creditor = cinfo['creditor']
        
        if not os.path.exists(base_dir):
            continue
            
        # Рекурсивно ищем файлы нужного формата
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                ext = os.path.splitext(file)[-1][1:].lower()
                full_path = os.path.join(root, file)
                
                # Фильтруем по формату и по списку уже обработанных
                if ext in allowed_exts and full_path not in processed_files:
                    files_for_processing.append({
                        'creditor': creditor,
                        'file': full_path,
                        'ext': ext
                    })

    # Логируем результат
    log_event(stage="filewalker", status="ok", count=len(files_for_processing))
    return files_for_processing 
# -*- coding: utf-8 -*-
"""
Модуль обработки и стандартизации Excel-файлов.
"""

import os
import pandas as pd
import openpyxl
import logging
import yaml
from openpyxl.styles import Alignment
from .state_manager import log_event, log_error

def load_yaml_list(filepath, key):
    """Загрузка эталонов из YAML"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data[key]
    except Exception as e:
        logging.error(f"Ошибка загрузки {filepath}: {e}")
        return []

def process_contract_folder(folder_path):
    """Обработка папки с договором"""
    contract_number = os.path.basename(folder_path)

    # Поиск Excel-файла
    excel_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.xlsx')]
    if not excel_files:
        log_error(stage="excel_processor", contract=contract_number, 
                 error_msg="Excel-файл не найден")
        return False

    excel_path = os.path.join(folder_path, excel_files[0])
    original_excel_path = os.path.join(folder_path, f"{contract_number}_original.xlsx")

    # Сохраняем копию оригинала для аудита
    if not os.path.exists(original_excel_path):
        try:
            import shutil
            shutil.copy2(excel_path, original_excel_path)
        except Exception as e:
            log_error(stage="excel_processor", contract=contract_number, 
                     error_msg=f"Ошибка копирования оригинального файла: {e}")

    new_excel_path = os.path.join(folder_path, f"{contract_number}.xlsx")
    if excel_path != new_excel_path:
        os.rename(excel_path, new_excel_path)
        log_event(stage="excel_processor", contract=contract_number, 
                 action="renamed", new_name=f"{contract_number}.xlsx")

    # Чтение структуры
    try:
        df = pd.read_excel(new_excel_path)
        input_columns_found = list(df.columns)
        log_event(stage="excel_processor", contract=contract_number, 
                 action="read", columns=input_columns_found)
    except Exception as e:
        log_error(stage="excel_processor", contract=contract_number, 
                 error_msg=f"Ошибка чтения Excel: {e}")
        return False

    # Загрузка эталонов
    try:
        INPUT_FIELDS = load_yaml_list('config/input_fields.yaml', 'input_fields')
        REQUIRED_FIELDS = load_yaml_list('config/required_fields.yaml', 'required_fields')
    except Exception as e:
        log_error(stage="excel_processor", contract=contract_number, 
                 error_msg=f"Ошибка загрузки эталонов: {e}")
        return False

    # Валидация исходных столбцов
    missing_in_input = [col for col in INPUT_FIELDS if col not in input_columns_found]
    if missing_in_input:
        log_event(stage="excel_processor", contract=contract_number, 
                 action="warning", missing_columns=missing_in_input)
    else:
        log_event(stage="excel_processor", contract=contract_number, 
                 action="validation", status="all_columns_present")

    # Добавляем недостающие итоговые столбцы
    for col in REQUIRED_FIELDS:
        if col not in df.columns:
            df[col] = ""
            log_event(stage="excel_processor", contract=contract_number, 
                     action="add_column", column=col)

    # Валидация итоговой структуры
    result_columns = list(df.columns)
    missing_in_result = [col for col in REQUIRED_FIELDS if col not in result_columns]
    if missing_in_result:
        log_error(stage="excel_processor", contract=contract_number, 
                 error_msg=f"После стандартизации НЕ ХВАТАЕТ столбцов: {missing_in_result}")
    else:
        log_event(stage="excel_processor", contract=contract_number, 
                 action="validation", status="final_structure_valid")

    # Упорядочиваем итоговую таблицу
    df = df[REQUIRED_FIELDS]

    # Сохраняем и форматируем
    temp_path = new_excel_path.replace(".xlsx", "_temp.xlsx")
    df.to_excel(temp_path, index=False)

    try:
        wb = openpyxl.load_workbook(temp_path)
        ws = wb.active
        for col in ws.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            col_letter = col[0].column_letter
            ws.column_dimensions[col_letter].width = max(10, max_len + 2)
            for cell in col:
                cell.alignment = Alignment(wrap_text=True, horizontal="left")
        wb.save(new_excel_path)
        os.remove(temp_path)
    except Exception as e:
        log_error(stage="excel_processor", contract=contract_number, 
                 error_msg=f"Ошибка форматирования: {e}")

    # Лог финальной структуры
    log_event(stage="excel_processor", contract=contract_number, 
             action="completed", final_columns=list(df.columns))
    return True

def preprocess_excels(input_dir="data/in", output_dir="data/in"):
    """Предобработка всех Excel-файлов в директории"""
    if not os.path.exists(input_dir):
        log_error(stage="excel_processor", error_msg=f"Входная папка не найдена: {input_dir}")
        return False
    
    processed_count = 0
    for root, dirs, files in os.walk(input_dir):
        for dir_name in dirs:
            folder_path = os.path.join(root, dir_name)
            if process_contract_folder(folder_path):
                processed_count += 1
    
    log_event(stage="excel_processor", action="batch_completed", processed_count=processed_count)
    return True 
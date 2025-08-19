# -*- coding: utf-8 -*-
"""
Загрузка конфигов и справочников системы.
"""

import os
import pandas as pd
import yaml
import json
import logging

CONFIG_LIST_CSV = [
    'formats.csv',
    'adresat.csv',
    'responsible.csv',
    'events.csv',
    'creditors_to_process.csv'
]

CONFIG_LIST_YAML = [
    'input_fields.yaml',
    'required_fields.yaml',
    'enrichment_fields.yaml',
    'validators.yaml',
    'ftp_settings.yaml',
    'mail_settings.yaml'
]

CONFIG_LIST_JSON = [
    'paths.json'
]

def load_configs(config_dir='config'):
    """Загружает все конфигурационные файлы"""
    configs = {}
    
    # Загрузка CSV-справочников
    for fname in CONFIG_LIST_CSV:
        path = os.path.join(config_dir, fname)
        if os.path.exists(path):
            try:
                configs[fname] = pd.read_csv(path, encoding='utf-8')
            except Exception as ex:
                logging.error(f'Ошибка чтения {fname}: {ex}')
                configs[fname] = None
        else:
            configs[fname] = None

    # Загрузка YAML-конфигов
    for fname in CONFIG_LIST_YAML:
        path = os.path.join(config_dir, fname)
        if os.path.exists(path):
            try:
                with open(path, encoding='utf-8') as f:
                    configs[fname] = yaml.safe_load(f)
            except Exception as ex:
                logging.error(f'Ошибка чтения {fname}: {ex}')
                configs[fname] = None
        else:
            configs[fname] = None

    # Загрузка JSON-конфигов
    for fname in CONFIG_LIST_JSON:
        path = os.path.join(config_dir, fname)
        if os.path.exists(path):
            try:
                with open(path, encoding='utf-8') as f:
                    configs[fname] = json.load(f)
            except Exception as ex:
                logging.error(f'Ошибка чтения {fname}: {ex}')
                configs[fname] = None
        else:
            configs[fname] = None

    return configs 
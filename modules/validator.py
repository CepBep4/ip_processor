# -*- coding: utf-8 -*-
"""
Модуль валидации конфигурации и файлов.
"""

def validate_all_configs(configs):
    """Валидация всех конфигурационных файлов"""
    errors = []
    
    # Проверяем наличие основных конфигов
    required_configs = ['input_fields.yaml', 'required_fields.yaml', 'ftp_settings.yaml']
    for config_name in required_configs:
        if configs.get(config_name) is None:
            errors.append(f"Отсутствует обязательный конфиг: {config_name}")
    
    return len(errors) == 0, errors 
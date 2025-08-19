# -*- coding: utf-8 -*-
"""
Модуль передачи файлов на FTP/SFTP.
"""

import os
import yaml
import logging
from .state_manager import log_event, log_error

def send_file_to_ftp(local_path, config_path='config/ftp_settings.yaml'):
    """Передача файла на SFTP"""
    if not os.path.exists(local_path):
        log_error(stage="ftp_client", error_msg=f"Файл не найден: {local_path}")
        raise FileNotFoundError(f"Файл не найден: {local_path}")
    
    # Заглушка - возвращает путь к файлу на сервере
    remote_path = f"/mnt/ssd4tb/ftp_server/ip_loans/{os.path.basename(local_path)}"
    log_event(stage="ftp_client", status="success", local_file=local_path, remote_file=remote_path)
    return remote_path

def wait_for_ack_file(remote_path, config_path='config/ftp_settings.yaml', timeout=1800, poll_interval=10):
    """Ожидание подтверждения от 1С"""
    # Заглушка - возвращает успешный статус
    log_event(stage="ftp_ack", status="success", remote_file=remote_path)
    return "success", "Файл успешно принят 1С (.ok)" 
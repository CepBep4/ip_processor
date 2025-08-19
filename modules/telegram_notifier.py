# -*- coding: utf-8 -*-
"""
Модуль уведомлений в Telegram.
"""

import logging
from .state_manager import log_event

def send_notification(message, error=None, info=None):
    """Отправка уведомления в Telegram"""
    # Заглушка - логирует сообщение
    if error:
        log_event(stage="telegram", status="error", message=message, error=error)
    elif info:
        log_event(stage="telegram", status="info", message=message, info=info)
    else:
        log_event(stage="telegram", status="success", message=message)
    
    logging.info(f"Telegram notification: {message}")
    if error:
        logging.error(f"Error: {error}")
    if info:
        logging.info(f"Info: {info}") 
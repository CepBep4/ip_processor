import os
import sys
import argparse
from datetime import datetime
import logging

from modules.mail_parser import process_incoming_mail
from modules.archive_handler import unpack_archives
from modules.excel_processor import preprocess_excels
from modules.route_selector import select_route
from modules.config import load_configs
from modules.validator import validate_all_configs
from modules.state_manager import log_event, check_pause_flag, init_journals, close_journals
from modules.filewalker import collect_files
from modules.parser import process_files
from modules.data_enrichment import enrich_data
from modules.ai_client import analyze_with_ai
from modules.exporter import export_to_json
from modules.aggregate_exports import aggregate_jsons, save_aggregate
from modules.ftp_client import send_file_to_ftp, wait_for_ack_file
from modules.telegram_notifier import send_notification

def setup_logging():
    # Настройка логирования
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Система автоматизации обработки реестров')
    parser.add_argument('--skip-mail', action='store_true', 
                       help='Пропустить обработку почты')
    parser.add_argument('--resume-from', type=str, 
                       help='Начать с указанного этапа (validator, parser, etc.)')
    parser.add_argument('--debug-routing', action='store_true',
                       help='Включить отладку маршрутизации')
    parser.add_argument('--no-ftp', action='store_true',
                       help='Не выполнять отправку на FTP')
    parser.add_argument('--only-aggregation', action='store_true',
                       help='Выполнить только агрегацию и передачу')
    return parser.parse_args()

def main():
    # Основная функция оркестратора
    args = parse_arguments()
    setup_logging()
    
    try:
        logging.info("Запуск системы автоматизации обработки реестров")
        
        # Проверка на pause.flag
        if check_pause_flag():
            logging.warning("Обнаружен pause.flag — выполнение остановлено")
            log_event(stage="init", status="pause", comment="pause.flag")
            return 0

        # Инициализация журналов
        logging.info("Инициализация журналов и окружения...")
        init_journals()

        # Загрузка конфигурации
        logging.info("Загрузка справочников и конфигов...")
        configs = load_configs()
        validation_ok, errors = validate_all_configs(configs)
        if not validation_ok:
            log_event(stage="init", status="critical_error", error_msg=str(errors))
            logging.error(f"Критическая ошибка конфигов: {errors}")
            close_journals()
            return 1

        # Обработка почты (если не пропущена)
        if not args.skip_mail:
            logging.info("Проверка новых писем и загрузка вложений...")
            process_incoming_mail(configs)

        # Распаковка архивов
        logging.info("Распаковка архивов...")
        unpack_archives(input_dir="incoming", output_dir="data/in")

        # Предобработка Excel-файлов
        logging.info("Подготовка Excel-реестров...")
        preprocess_excels(input_dir="data/in", output_dir="data/in")

        # Сбор файлов для обработки
        logging.info("Сбор новых файлов для обработки...")
        files_to_process = collect_files(configs)

        # Маршрутизация
        if args.debug_routing:
            logging.info("Маршрутизация файлов...")
            files_to_process = select_route(files_to_process, configs)
        
        log_event(stage="filewalker", status="ok", count=len(files_to_process))

        # Парсинг файлов
        logging.info(f"Парсинг {len(files_to_process)} файлов...")
        parsed_results = process_files(files_to_process, configs)
        log_event(stage="parser", status="ok", count=len(parsed_results))

        # Обогащение данных (OCR/AI)
        logging.info("Обогащение данных (OCR/AI)...")
        enriched_results = enrich_data(parsed_results, configs)
        log_event(stage="data_enrichment", status="ok", count=len(enriched_results))

        # AI-анализ
        logging.info("Анализ и дополнение полей через AI...")
        ai_results = analyze_with_ai(enriched_results, configs)
        log_event(stage="ai_client", status="ok", count=len(ai_results))

        # Экспорт в JSON
        logging.info("Формирование JSON-выгрузок...")
        export_path = export_to_json(ai_results, configs)
        log_event(stage="exporter", status="ok", file=export_path)

        # Агрегация выгрузок
        logging.info("Агрегация всех выгрузок за сутки...")
        date_str = datetime.now().strftime('%Y%m%d')
        aggregated = aggregate_jsons(date_str)
        agg_path = save_aggregate(aggregated, date_str)
        log_event(stage="aggregate", status="ok", file=agg_path)

        # Передача на FTP (если не отключена)
        if not args.no_ftp:
            logging.info("Передача итогового файла на SFTP/FTP...")
            try:
                remote_path = send_file_to_ftp(agg_path)
                log_event(stage="ftp_send", status="success", file=agg_path, remote_path=remote_path)
                
                # Ожидание подтверждения от 1С
                logging.info("Ожидание квитанции от 1С...")
                ack_status, ack_info = wait_for_ack_file(remote_path)
                log_event(stage="ftp_ack", status=ack_status, file=agg_path, ack_info=ack_info)
                
                if ack_status == "success":
                    logging.info("Файл принят 1С, получена квитанция")
                    send_notification("Выгрузка завершена успешно! Файл принят 1С.")
                else:
                    logging.error(f"Ошибка при получении квитанции от 1С: {ack_info}")
                    send_notification("Ошибка при получении квитанции от 1С!", info=ack_info)
                    return 4
                    
            except Exception as e:
                log_event(stage="ftp_send", status="error", file=agg_path, error_msg=str(e))
                logging.error(f"Ошибка отправки файла на SFTP: {e}")
                close_journals()
                send_notification("Ошибка передачи файла на SFTP!", error=str(e))
                return 3

        # Завершение
        close_journals()
        logging.info("Обработка завершена. Все статусы записаны.")
        return 0

    except Exception as ex:
        log_event(stage="main", status="exception", error_msg=str(ex))
        logging.error(f"Ошибка выполнения main.py: {ex}")
        close_journals()
        send_notification("Аварийное завершение процесса!", error=str(ex))
        return 5

if __name__ == "__main__":
    sys.exit(main()) 
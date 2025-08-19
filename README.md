# Система автоматизации обработки реестров по исполнительным производствам

## Описание

Система автоматизации предназначена для обработки входящих архивов и реестров от разных кредиторов (Valberis, Ozon и др.) по заранее заданным маршрутам. Система автоматизирует весь процесс от получения писем до передачи данных в 1С через FTP.

## Архитектура

Проект построен по модульному принципу:

- `main.py` - главный оркестратор системы
- `modules/` - основные модули обработки
- `config/` - конфигурационные файлы
- `logs/` - логи системы
- `data/` - рабочие данные
- `exports/` - экспортированные файлы

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте конфигурационные файлы в папке `config/`

## Использование

### Основной запуск
```bash
python main.py
```

### Запуск с параметрами
```bash
python main.py --skip-mail --no-ftp
```

### Доступные параметры
- `--skip-mail` - пропустить обработку почты
- `--resume-from <stage>` - начать с указанного этапа
- `--debug-routing` - включить отладку маршрутизации
- `--no-ftp` - не выполнять отправку на FTP
- `--only-aggregation` - выполнить только агрегацию

## Конфигурация

### Настройка почты
Отредактируйте `config/mail_settings.yaml`:
```yaml
host: "imap.gmail.com"
username: "your_email@gmail.com"
password: "your_app_password"
```

### Настройка FTP
Отредактируйте `config/ftp_settings.yaml`:
```yaml
ftp:
  host: "your_ftp_server"
  port: 22
  user: "ftpuser"
  password: "password"
```

### Настройка полей
- `config/input_fields.yaml` - входные поля
- `config/required_fields.yaml` - обязательные поля
- `config/enrichment_fields.yaml` - поля для обогащения

## Структура проекта

```
├── main.py                 # Главный оркестратор
├── modules/                # Модули системы
│   ├── mail_parser.py      # Обработка почты
│   ├── archive_handler.py  # Распаковка архивов
│   ├── excel_processor.py  # Обработка Excel
│   ├── parser.py           # Парсинг файлов
│   ├── validator.py        # Валидация
│   ├── exporter.py         # Экспорт в JSON
│   ├── ftp_client.py       # Передача на FTP
│   └── telegram_notifier.py # Уведомления
├── config/                 # Конфигурация
├── logs/                   # Логи
├── data/                   # Рабочие данные
├── exports/                # Экспорт
└── requirements.txt        # Зависимости
```

## Логирование

Система ведет подробные логи в папке `logs/`:
- `main.log` - основной лог
- `process_log.json` - события процесса
- `error_log.json` - ошибки
- `duplicates_log.json` - дубликаты
- `not_processed.json` - необработанные файлы

## Управление системой

### Пауза обработки
Создайте файл `logs/pause.flag` для остановки системы

### Мониторинг
Система отправляет уведомления в Telegram о статусе обработки

## Разработка

### Добавление нового кредитора
1. Добавьте запись в `config/creditors_to_process.csv`
2. Создайте схему полей в `config/excel_fields_<creditor>.yaml`
3. Настройте маршрутизацию в `config/paths.json`

### Расширение функциональности
Модули системы легко расширяются. Каждый модуль имеет четкий интерфейс и логирует свои действия.

## Требования

- Python 3.8+
- Tesseract OCR (для обработки изображений)
- Доступ к IMAP серверу
- Доступ к SFTP серверу

## Лицензия

Внутренний проект компании. # ip_processor

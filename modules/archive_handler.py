import os
import shutil
import zipfile
import logging
from .state_manager import log_event, log_error

def is_archive(file_path):
    """Проверка - архив или нет"""
    ext = os.path.splitext(file_path)[-1].lower()
    return ext in ['.zip', '.rar']

def extract_archive(archive_path, dest_dir):
    """Распаковывает архив (ZIP/RAR) во временную папку"""
    extracted_files = []
    try:
        if archive_path.lower().endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(dest_dir)
                extracted_files = [os.path.join(dest_dir, name) for name in zf.namelist()]
        elif archive_path.lower().endswith('.rar'):
            # Для RAR файлов нужна библиотека rarfile
            try:
                import rarfile
                with rarfile.RarFile(archive_path, 'r') as rf:
                    rf.extractall(dest_dir)
                    extracted_files = [os.path.join(dest_dir, name) for name in rf.namelist()]
            except ImportError:
                log_error(stage="archive_handler", archive=archive_path, 
                         error_msg="Библиотека rarfile не установлена")
                return []
        
        log_event(stage="archive_handler", status="ok", archive=archive_path, 
                 dest=dest_dir, count=len(extracted_files))
    except Exception as ex:
        log_error(stage="archive_handler", archive=archive_path, error_msg=str(ex))
    return extracted_files

def cleanup_folder(folder, allowed_exts):
    # Удаляет из папки все файлы, не соответствующие списку разрешённых расширений
    removed = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            ext = os.path.splitext(file)[-1].lower()
            if ext not in allowed_exts:
                try:
                    os.remove(os.path.join(root, file))
                    removed += 1
                except Exception:
                    continue
    log_event(stage="archive_handler", status="cleanup", folder=folder, removed=removed)
    return removed

def unpack_archives(input_dir="incoming", output_dir="data/in"):
    # Находит архивы в папке input_dir, распаковывает их в output_dir
    if not os.path.exists(input_dir):
        log_error(stage="archive_handler", error_msg=f"Входная папка не найдена: {input_dir}")
        return []
    
    allowed_exts = ['.xlsx', '.xls', '.pdf', '.docx', '.jpg', '.jpeg', '.png']
    new_files = []
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if is_archive(file_path):
                # Создаём уникальную рабочую папку для архива
                extract_dir = os.path.join(output_dir, os.path.splitext(file)[0])
                os.makedirs(extract_dir, exist_ok=True)
                extracted = extract_archive(file_path, extract_dir)
                cleanup_folder(extract_dir, allowed_exts)
                new_files.extend(extracted)
    
    return new_files 
"""
Потокобезопасный обработчик JSON файлов с использованием Lock.
Предотвращает race condition при одновременной записи из разных потоков.
"""
import json
import threading
from pathlib import Path
from typing import Any

# Глобальный Lock для осуществления синхронизации всех операций с файлами
_file_lock = threading.Lock()


def read_json(file_path: str) -> Any:
    """
    Безопасное чтение JSON файла с блокировкой.
    
    Args:
        file_path: Путь к JSON файлу
        
    Returns:
        Распарсенные данные из JSON файла
    """
    with _file_lock:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Ошибка парсинга JSON файла {file_path}", e.doc, e.pos)


def write_json(file_path: str, data: Any, indent: int = None) -> None:
    """
    Безопасная запись JSON файла с блокировкой.
    Использует временный файл для атомарной операции.
    
    Args:
        file_path: Путь к JSON файлу
        data: Данные для записи
        indent: Количество пробелов для форматирования (по умолчанию - без форматирования)
    """
    with _file_lock:
        # Преобразуем путь использованием pathlib для получения папки
        path = Path(file_path)
        temp_path = path.parent / f"{path.name}.tmp"
        
        try:
            # Пишем во временный файл
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            # Заменяем оригинальный файл временным (атомарная операция на Windows)
            temp_path.replace(path)
        except Exception as e:
            # Удаляем временный файл в случае ошибки
            if temp_path.exists():
                temp_path.unlink()
            raise e


def update_json(file_path: str, update_func, *args, **kwargs) -> Any:
    """
    Безопасное обновление JSON файла с использованием callback функции.
    Функция читает файл, применяет update_func и пишет результат.
    
    Args:
        file_path: Путь к JSON файлу
        update_func: Функция, которая принимает текущие данные и возвращает обновленные
        *args, **kwargs: Дополнительные аргументы для update_func
        
    Returns:
        Результат работы update_func
    """
    with _file_lock:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Применяем функцию обновления
        result = update_func(data, *args, **kwargs)
        
        # Пишем обновленные данные
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=None, ensure_ascii=False)
        
        return result

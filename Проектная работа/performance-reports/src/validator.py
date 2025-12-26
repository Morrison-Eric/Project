"""
Валидация данных и конфигурации
"""

import os
import json
from typing import Dict, Any
from datetime import datetime


class ValidationError(Exception):
    """Ошибка валидации"""
    pass


def validate_config(config: Dict[str, Any]) -> bool:
    """Валидация конфигурации"""
    required_sections = ['metrics', 'reporting', 'scheduling', 'paths', 'thresholds']
    
    for section in required_sections:
        if section not in config:
            raise ValidationError(f"Отсутствует секция конфигурации: {section}")
    
    # Проверка путей
    for path in config['paths'].values():
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            raise ValidationError(f"Не удалось создать директорию {path}: {e}")
    
    # Проверка порогов
    thresholds = config['thresholds']
    for key, value in thresholds.items():
        if not isinstance(value, (int, float)):
            raise ValidationError(f"Порог {key} должен быть числом")
        if not 0 <= value <= 100:
            raise ValidationError(f"Порог {key} должен быть между 0 и 100")
    
    return True


def validate_metrics_file(filepath: str) -> bool:
    """Валидация файла с метриками"""
    if not os.path.exists(filepath):
        raise ValidationError(f"Файл не найден: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValidationError("Файл метрик должен содержать список")
        
        if len(data) == 0:
            raise ValidationError("Файл метрик пуст")
        
        # Проверка структуры первой записи
        first_item = data[0]
        required_keys = ['timestamp', 'cpu', 'memory', 'disk', 'network']
        
        for key in required_keys:
            if key not in first_item:
                raise ValidationError(f"Отсутствует ключ {key} в метриках")
        
        return True
        
    except json.JSONDecodeError as e:
        raise ValidationError(f"Ошибка формата JSON: {e}")
    except Exception as e:
        raise ValidationError(f"Ошибка при чтении файла: {e}")


def validate_date_range(start_date: str, end_date: str) -> bool:
    """Валидация диапазона дат"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start > end:
            raise ValidationError("Дата начала должна быть раньше даты окончания")
        
        if (end - start).days > 365:
            raise ValidationError("Диапазон дат не должен превышать 1 год")
        
        return True
    except ValueError as e:
        raise ValidationError(f"Неверный формат даты: {e}")


def validate_output_path(path: str) -> bool:
    """Валидация пути для сохранения"""
    try:
        directory = os.path.dirname(path) or '.'
        os.makedirs(directory, exist_ok=True)
        
        # Проверка доступности на запись
        test_file = os.path.join(directory, '.write_test')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        return True
    except Exception as e:
        raise ValidationError(f"Путь недоступен для записи: {e}")
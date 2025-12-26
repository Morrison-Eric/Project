"""
Конфигурация системы отчетов
"""

import os
from datetime import time

# Базовая конфигурация
DEFAULT_CONFIG = {
    'metrics': {
        'cpu': True,
        'memory': True,
        'disk': True,
        'network': True,
        'processes': False
    },
    'reporting': {
        'format': 'text',
        'save_charts': True,
        'charts_dir': 'reports/charts',
        'reports_dir': 'reports',
        'max_history': 30  # дней
    },
    'scheduling': {
        'daily_time': time(9, 0),  # 9:00 утра
        'weekly_day': 'monday',
        'retention_days': 7
    },
    'paths': {
        'reports': 'reports',
        'charts': 'reports/charts',
        'logs': 'logs',
        'data': 'data'
    },
    'thresholds': {
        'cpu_warning': 80,  # %
        'memory_warning': 85,  # %
        'disk_warning': 90  # %
    }
}


def ensure_directories():
    """Создание необходимых директорий"""
    paths = DEFAULT_CONFIG['paths']
    
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    
    # Специальные директории
    os.makedirs(DEFAULT_CONFIG['reporting']['charts_dir'], exist_ok=True)
    os.makedirs(DEFAULT_CONFIG['reporting']['reports_dir'], exist_ok=True)


def get_config():
    """Получение конфигурации"""
    ensure_directories()
    return DEFAULT_CONFIG
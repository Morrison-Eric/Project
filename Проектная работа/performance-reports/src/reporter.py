"""
Генерация отчетов в различных форматах
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from config import get_config


class ReportGenerator:
    """Генератор отчетов"""
    
    def __init__(self):
        self.config = get_config()
        
    def generate_report(self, metrics_file: str, report_type: str = 'text') -> str:
        """Генерация отчета указанного типа"""
        metrics = self._load_metrics(metrics_file)
        
        if report_type == 'text':
            return self._generate_text_report(metrics)
        elif report_type == 'html':
            return self._generate_html_report(metrics)
        elif report_type == 'json':
            return self._generate_json_report(metrics)
        else:
            raise ValueError(f"Неизвестный тип отчета: {report_type}")
    
    def _generate_text_report(self, metrics: List[Dict]) -> str:
        """Генерация текстового отчета"""
        if not metrics:
            return "Нет данных для отчета"
        
        last_metric = metrics[-1]
        first_metric = metrics[0]
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ СИСТЕМЫ")
        report_lines.append("=" * 60)
        report_lines.append(f"Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Период измерений: {len(metrics)} записей")
        report_lines.append(f"Первое измерение: {first_metric['timestamp']}")
        report_lines.append(f"Последнее измерение: {last_metric['timestamp']}")
        report_lines.append("")
        
        # CPU
        cpu = last_metric['cpu']
        report_lines.append("ЗАГРУЗКА CPU:")
        report_lines.append(f"  Общая загрузка: {cpu['percent_total']:.1f}%")
        report_lines.append(f"  Ядер: {cpu['cores']}")
        if cpu['frequency_current']:
            report_lines.append(f"  Частота: {cpu['frequency_current']:.0f} МГц")
        report_lines.append("")
        
        # Memory
        memory = last_metric['memory']
        report_lines.append("ПАМЯТЬ:")
        report_lines.append(f"  Оперативная память: {memory['percent']:.1f}%")
        report_lines.append(f"  Использовано: {self._bytes_to_gb(memory['used']):.1f} ГБ")
        report_lines.append(f"  Всего: {self._bytes_to_gb(memory['total']):.1f} ГБ")
        report_lines.append(f"  Своп: {memory['swap_percent']:.1f}%")
        report_lines.append("")
        
        # Disk
        disk = last_metric['disk']
        report_lines.append("ДИСК:")
        report_lines.append(f"  Использовано: {disk['percent']:.1f}%")
        report_lines.append(f"  Свободно: {self._bytes_to_gb(disk['free']):.1f} ГБ")
        report_lines.append(f"  Всего: {self._bytes_to_gb(disk['total']):.1f} ГБ")
        report_lines.append(f"  Прочитано: {self._bytes_to_gb(disk['read_bytes']):.2f} ГБ")
        report_lines.append(f"  Записано: {self._bytes_to_gb(disk['write_bytes']):.2f} ГБ")
        report_lines.append("")
        
        # Network
        network = last_metric['network']
        report_lines.append("СЕТЬ:")
        report_lines.append(f"  Отправлено: {self._bytes_to_mb(network['bytes_sent']):.1f} МБ")
        report_lines.append(f"  Получено: {self._bytes_to_mb(network['bytes_recv']):.1f} МБ")
        report_lines.append(f"  Соединений: {network['connections']}")
        report_lines.append("")
        
        # System
        system = last_metric['system']
        uptime = timedelta(seconds=system['uptime_seconds'])
        report_lines.append("СИСТЕМА:")
        report_lines.append(f"  Время работы: {str(uptime).split('.')[0]}")
        report_lines.append(f"  Пользователей: {system['users']}")
        report_lines.append(f"  Процессов: {system['processes']}")
        report_lines.append("")
        
        # Проверка порогов
        report_lines.append("ПРОВЕРКА ПОРОГОВ:")
        thresholds = self.config['thresholds']
        
        if cpu['percent_total'] > thresholds['cpu_warning']:
            report_lines.append(f"  ⚠️  CPU: {cpu['percent_total']:.1f}% > {thresholds['cpu_warning']}%")
        
        if memory['percent'] > thresholds['memory_warning']:
            report_lines.append(f"  ⚠️  Память: {memory['percent']:.1f}% > {thresholds['memory_warning']}%")
        
        if disk['percent'] > thresholds['disk_warning']:
            report_lines.append(f"  ⚠️  Диск: {disk['percent']:.1f}% > {thresholds['disk_warning']}%")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _generate_html_report(self, metrics: List[Dict]) -> str:
        """Генерация HTML отчета"""
        if not metrics:
            return "<html><body>Нет данных</body></html>"
        
        last_metric = metrics[-1]
        cpu = last_metric['cpu']
        memory = last_metric['memory']
        disk = last_metric['disk']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Отчет о производительности</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .warning {{ background-color: #fff3cd; border-color: #ffeaa7; }}
                .good {{ background-color: #d4edda; border-color: #c3e6cb; }}
                .value {{ font-weight: bold; font-size: 1.2em; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Отчет о производительности системы</h1>
                <p class="timestamp">Сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric {self._get_status_class(cpu['percent_total'], 'cpu')}">
                <h2>Загрузка CPU</h2>
                <p class="value">{cpu['percent_total']:.1f}%</p>
                <p>Ядер: {cpu['cores']} | Частота: {cpu['frequency_current'] or 'N/A'} МГц</p>
            </div>
            
            <div class="metric {self._get_status_class(memory['percent'], 'memory')}">
                <h2>Оперативная память</h2>
                <p class="value">{memory['percent']:.1f}%</p>
                <p>Использовано: {self._bytes_to_gb(memory['used']):.1f} ГБ из {self._bytes_to_gb(memory['total']):.1f} ГБ</p>
            </div>
            
            <div class="metric {self._get_status_class(disk['percent'], 'disk')}">
                <h2>Дисковое пространство</h2>
                <p class="value">{disk['percent']:.1f}%</p>
                <p>Свободно: {self._bytes_to_gb(disk['free']):.1f} ГБ из {self._bytes_to_gb(disk['total']):.1f} ГБ</p>
            </div>
            
            <div class="metric">
                <h2>Сетевая активность</h2>
                <p>Отправлено: {self._bytes_to_mb(last_metric['network']['bytes_sent']):.1f} МБ</p>
                <p>Получено: {self._bytes_to_mb(last_metric['network']['bytes_recv']):.1f} МБ</p>
                <p>Активных соединений: {last_metric['network']['connections']}</p>
            </div>
            
            <div class="metric">
                <h2>🖥️ Системная информация</h2>
                <p>Время работы системы: {timedelta(seconds=last_metric['system']['uptime_seconds'])}</p>
                <p>Активных пользователей: {last_metric['system']['users']}</p>
                <p>Запущенных процессов: {last_metric['system']['processes']}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_json_report(self, metrics: List[Dict]) -> str:
        """Генерация JSON отчета"""
        if not metrics:
            return json.dumps({"error": "Нет данных"}, indent=2)
        
        last_metric = metrics[-1]
        summary = {
            "timestamp": datetime.now().isoformat(),
            "period": {
                "start": metrics[0]['timestamp'],
                "end": last_metric['timestamp'],
                "measurements": len(metrics)
            },
            "summary": {
                "cpu_percent": last_metric['cpu']['percent_total'],
                "memory_percent": last_metric['memory']['percent'],
                "disk_percent": last_metric['disk']['percent'],
                "network_sent_mb": self._bytes_to_mb(last_metric['network']['bytes_sent']),
                "network_recv_mb": self._bytes_to_mb(last_metric['network']['bytes_recv'])
            },
            "thresholds": self.config['thresholds'],
            "alerts": self._check_thresholds(last_metric)
        }
        
        return json.dumps(summary, indent=2, default=str)
    
    def _get_status_class(self, value: float, metric_type: str) -> str:
        """Определение класса CSS на основе значения метрики"""
        thresholds = self.config['thresholds']
        
        if metric_type == 'cpu' and value > thresholds['cpu_warning']:
            return 'warning'
        elif metric_type == 'memory' and value > thresholds['memory_warning']:
            return 'warning'
        elif metric_type == 'disk' and value > thresholds['disk_warning']:
            return 'warning'
        
        return 'good'
    
    def _check_thresholds(self, metric: Dict) -> List[str]:
        """Проверка превышения пороговых значений"""
        alerts = []
        thresholds = self.config['thresholds']
        
        if metric['cpu']['percent_total'] > thresholds['cpu_warning']:
            alerts.append(f"CPU загрузка {metric['cpu']['percent_total']:.1f}% превышает порог {thresholds['cpu_warning']}%")
        
        if metric['memory']['percent'] > thresholds['memory_warning']:
            alerts.append(f"Использование памяти {metric['memory']['percent']:.1f}% превышает порог {thresholds['memory_warning']}%")
        
        if metric['disk']['percent'] > thresholds['disk_warning']:
            alerts.append(f"Использование диска {metric['disk']['percent']:.1f}% превышает порог {thresholds['disk_warning']}%")
        
        return alerts
    
    def _bytes_to_gb(self, bytes_value: int) -> float:
        """Конвертация байтов в гигабайты"""
        return bytes_value / (1024 ** 3)
    
    def _bytes_to_mb(self, bytes_value: int) -> float:
        """Конвертация байтов в мегабайты"""
        return bytes_value / (1024 ** 2)
    
    def _load_metrics(self, metrics_file: str) -> List[Dict]:
        """Загрузка метрик из файла"""
        with open(metrics_file, 'r') as f:
            return json.load(f)
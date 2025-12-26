"""
Планировщик периодических отчетов
"""

import schedule
import time
import threading
from datetime import datetime
from .collector import SystemMetricsCollector
from .reporter import ReportGenerator
from .visualizer import MetricsVisualizer
from config import get_config


class ReportScheduler:
    """Планировщик отчетов"""
    
    def __init__(self):
        self.config = get_config()
        self.collector = SystemMetricsCollector()
        self.reporter = ReportGenerator()
        self.visualizer = MetricsVisualizer()
        self.running = False
        
    def run_once(self, frequency: str):
        """Однократный запуск отчета"""
        print(f"Запуск {frequency} отчета...")
        
        # Сбор метрик
        metrics = self.collector.collect_continuous(count=60, interval=1)
        
        # Сохранение метрик
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = f"data/metrics_{frequency}_{timestamp}.json"
        self.collector.save_metrics(metrics, metrics_file)
        
        # Генерация отчета
        report = self.reporter.generate_report(metrics_file, 'text')
        
        # Сохранение отчета
        report_file = f"reports/{frequency}_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Создание графиков
        chart_file = self.visualizer.create_chart(metrics_file, 'all')
        
        print(f"Отчет сохранен: {report_file}")
        print(f"График сохранен: {chart_file}")
        
        return report_file, chart_file
    
    def run_continuous(self, frequency: str):
        """Непрерывный запуск отчетов по расписанию"""
        print(f"Запуск планировщика ({frequency} отчеты)...")
        print("Нажмите Ctrl+C для остановки")
        
        if frequency == 'hourly':
            schedule.every().hour.at(":00").do(self._scheduled_task, 'hourly')
        elif frequency == 'daily':
            schedule.every().day.at("09:00").do(self._scheduled_task, 'daily')
        elif frequency == 'weekly':
            schedule.every().monday.at("09:00").do(self._scheduled_task, 'weekly')
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
        except KeyboardInterrupt:
            print("\nОстановка планировщика...")
            self.running = False
    
    def _scheduled_task(self, frequency: str):
        """Задача по расписанию"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск {frequency} задачи...")
        
        try:
            self.run_once(frequency)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {frequency} задача завершена")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ошибка: {e}")
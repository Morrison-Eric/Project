"""
Визуализация метрик в виде графиков
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import os
from typing import List, Dict, Any
from config import get_config


class MetricsVisualizer:
    """Создание графиков и диаграмм"""
    
    def __init__(self):
        self.config = get_config()
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def create_chart(self, metrics_file: str, chart_type: str, 
                    output_file: str = None) -> str:
        """Создание графика указанного типа"""
        metrics = self._load_metrics(metrics_file)
        
        if chart_type == 'cpu':
            return self._create_cpu_chart(metrics, output_file)
        elif chart_type == 'memory':
            return self._create_memory_chart(metrics, output_file)
        elif chart_type == 'disk':
            return self._create_disk_chart(metrics, output_file)
        elif chart_type == 'network':
            return self._create_network_chart(metrics, output_file)
        elif chart_type == 'all':
            return self._create_comprehensive_chart(metrics, output_file)
        else:
            raise ValueError(f"Неизвестный тип графика: {chart_type}")
    
    def _create_cpu_chart(self, metrics: List[Dict], output_file: str = None) -> str:
        """График загрузки CPU"""
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        cpu_values = [m['cpu']['percent_total'] for m in metrics]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Общая загрузка CPU
        ax1.plot(timestamps, cpu_values, 'b-', linewidth=2)
        ax1.set_title('Общая загрузка CPU', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Загрузка (%)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # Загрузка по ядрам (последнее измерение)
        if metrics:
            last_cpu = metrics[-1]['cpu']['percent_per_core']
            cores = range(1, len(last_cpu) + 1)
            ax2.bar(cores, last_cpu, color='steelblue', alpha=0.7)
            ax2.set_title('Загрузка по ядрам (последнее измерение)', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Номер ядра', fontsize=12)
            ax2.set_ylabel('Загрузка (%)', fontsize=12)
            ax2.set_xticks(cores)
        
        plt.tight_layout()
        
        if not output_file:
            output_file = os.path.join(self.config['reporting']['charts_dir'],
                                     f'cpu_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def _create_memory_chart(self, metrics: List[Dict], output_file: str = None) -> str:
        """График использования памяти"""
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        memory_values = [m['memory']['percent'] for m in metrics]
        swap_values = [m['memory']['swap_percent'] for m in metrics]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Оперативная память
        ax1.plot(timestamps, memory_values, 'g-', linewidth=2, label='Оперативная память')
        ax1.fill_between(timestamps, 0, memory_values, alpha=0.3, color='green')
        ax1.set_title('Использование оперативной памяти', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Использование (%)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        # Своп память
        if any(swap > 0 for swap in swap_values):
            ax2.plot(timestamps, swap_values, 'r-', linewidth=2, label='Своп память')
            ax2.fill_between(timestamps, 0, swap_values, alpha=0.3, color='red')
            ax2.set_title('Использование своп памяти', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Использование (%)', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        else:
            ax2.text(0.5, 0.5, 'Своп память не используется', 
                    ha='center', va='center', fontsize=12)
            ax2.axis('off')
        
        plt.tight_layout()
        
        if not output_file:
            output_file = os.path.join(self.config['reporting']['charts_dir'],
                                     f'memory_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def _create_disk_chart(self, metrics: List[Dict], output_file: str = None) -> str:
        """График использования диска"""
        if not metrics:
            raise ValueError("Нет данных для построения графика")
        
        last_metric = metrics[-1]
        disk = last_metric['disk']
        
        labels = ['Использовано', 'Свободно']
        sizes = [disk['used'], disk['free']]
        colors = ['#ff9999', '#66b3ff']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Круговая диаграмма
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, wedgeprops={'edgecolor': 'white'})
        ax1.set_title(f'Использование диска: {disk["percent"]:.1f}%', 
                     fontsize=14, fontweight='bold')
        
        # Гистограмма IO
        io_labels = ['Чтение', 'Запись']
        io_read = disk['read_bytes'] / (1024**3)  # в GB
        io_write = disk['write_bytes'] / (1024**3)  # в GB
        
        ax2.bar(io_labels, [io_read, io_write], color=['blue', 'orange'])
        ax2.set_title('Операции ввода-вывода', fontsize=14, fontweight='bold')
        ax2.set_ylabel('ГБ', fontsize=12)
        
        plt.tight_layout()
        
        if not output_file:
            output_file = os.path.join(self.config['reporting']['charts_dir'],
                                     f'disk_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def _create_network_chart(self, metrics: List[Dict], output_file: str = None) -> str:
        """График сетевой активности"""
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        
        # Конвертируем байты в мегабайты
        sent_mb = [m['network']['bytes_sent'] / (1024**2) for m in metrics]
        recv_mb = [m['network']['bytes_recv'] / (1024**2) for m in metrics]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(timestamps, sent_mb, 'b-', linewidth=2, label='Отправлено')
        ax.plot(timestamps, recv_mb, 'g-', linewidth=2, label='Получено')
        
        ax.set_title('Сетевая активность', fontsize=14, fontweight='bold')
        ax.set_ylabel('МБ', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
        plt.tight_layout()
        
        if not output_file:
            output_file = os.path.join(self.config['reporting']['charts_dir'],
                                     f'network_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def _create_comprehensive_chart(self, metrics: List[Dict], output_file: str = None) -> str:
        """Комплексный график всех метрик"""
        timestamps = [datetime.fromisoformat(m['timestamp']) for m in metrics]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # CPU
        cpu_values = [m['cpu']['percent_total'] for m in metrics]
        ax1.plot(timestamps, cpu_values, 'r-', linewidth=1.5)
        ax1.set_title('Загрузка CPU', fontsize=12)
        ax1.set_ylabel('%')
        ax1.grid(True, alpha=0.3)
        
        # Memory
        memory_values = [m['memory']['percent'] for m in metrics]
        ax2.plot(timestamps, memory_values, 'g-', linewidth=1.5)
        ax2.set_title('Использование памяти', fontsize=12)
        ax2.set_ylabel('%')
        ax2.grid(True, alpha=0.3)
        
        # Disk
        disk_values = [m['disk']['percent'] for m in metrics]
        ax3.plot(timestamps, disk_values, 'b-', linewidth=1.5)
        ax3.set_title('Использование диска', fontsize=12)
        ax3.set_ylabel('%')
        ax3.grid(True, alpha=0.3)
        
        # Network
        network_sent = [m['network']['bytes_sent'] / (1024**2) for m in metrics]
        network_recv = [m['network']['bytes_recv'] / (1024**2) for m in metrics]
        ax4.plot(timestamps, network_sent, 'orange', linewidth=1.5, label='Отправлено')
        ax4.plot(timestamps, network_recv, 'purple', linewidth=1.5, label='Получено')
        ax4.set_title('Сетевая активность', fontsize=12)
        ax4.set_ylabel('МБ')
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        # Форматирование осей времени
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.suptitle('Комплексный отчет о производительности', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if not output_file:
            output_file = os.path.join(self.config['reporting']['charts_dir'],
                                     f'comprehensive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    def _load_metrics(self, metrics_file: str) -> List[Dict]:
        """Загрузка метрик из файла"""
        with open(metrics_file, 'r') as f:
            return json.load(f)
"""
Сборщик метрик производительности системы
"""

import psutil
import time
import json
from datetime import datetime
from typing import Dict, List, Any


class SystemMetricsCollector:
    """Сбор метрик производительности системы"""
    
    def __init__(self):
        self.metrics_history = []
        
    def collect_single(self) -> Dict[str, Any]:
        """Сбор одного набора метрик"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'cpu': self._get_cpu_metrics(),
            'memory': self._get_memory_metrics(),
            'disk': self._get_disk_metrics(),
            'network': self._get_network_metrics(),
            'system': self._get_system_metrics()
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def collect_continuous(self, count: int = 10, interval: float = 1.0) -> List[Dict]:
        """Непрерывный сбор метрик"""
        metrics_list = []
        
        for i in range(count):
            if i > 0:
                time.sleep(interval)
                
            print(f"Сбор {i+1}/{count}...")
            metrics = self.collect_single()
            metrics_list.append(metrics)
            
        return metrics_list
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Метрики CPU"""
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        return {
            'percent_per_core': cpu_percent,
            'percent_total': sum(cpu_percent) / len(cpu_percent),
            'cores': len(cpu_percent),
            'frequency_current': cpu_freq.current if cpu_freq else None,
            'frequency_min': cpu_freq.min if cpu_freq else None,
            'frequency_max': cpu_freq.max if cpu_freq else None
        }
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Метрики памяти"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Метрики диска"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        return {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'percent': disk_usage.percent,
            'read_bytes': disk_io.read_bytes if disk_io else 0,
            'write_bytes': disk_io.write_bytes if disk_io else 0,
            'read_count': disk_io.read_count if disk_io else 0,
            'write_count': disk_io.write_count if disk_io else 0
        }
    
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Метрики сети"""
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections': len(psutil.net_connections())
        }
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Системные метрики"""
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'users': len(psutil.users()),
            'processes': len(psutil.pids())
        }
    
    def save_metrics(self, metrics: List[Dict], filename: str = 'metrics.json'):
        """Сохранение метрик в файл"""
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
    
    def load_metrics(self, filename: str = 'metrics.json') -> List[Dict]:
        """Загрузка метрик из файла"""
        with open(filename, 'r') as f:
            return json.load(f)
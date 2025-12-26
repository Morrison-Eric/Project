#!/usr/bin/env python3
"""
Performance Reports - CLI инструмент для мониторинга производительности системы
"""

import argparse
import sys
from datetime import datetime
from src.collector import SystemMetricsCollector
from src.visualizer import MetricsVisualizer
from src.reporter import ReportGenerator
from src.scheduler import ReportScheduler
from src.validator import validate_config
from config import DEFAULT_CONFIG


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Система отчетов о производительности',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py collect -n 5 -i 2     # Собрать 5 метрик с интервалом 2 сек
  python main.py report -t html         # Сгенерировать HTML отчет
  python main.py visualize -t cpu       # Построить график загрузки CPU
  python main.py schedule daily         # Запустить ежедневные отчеты
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда collect
    collect_parser = subparsers.add_parser('collect', help='Сбор метрик')
    collect_parser.add_argument('-n', '--count', type=int, default=10, 
                              help='Количество измерений')
    collect_parser.add_argument('-i', '--interval', type=float, default=1.0,
                              help='Интервал между измерениями (секунды)')
    collect_parser.add_argument('-o', '--output', default='metrics.json',
                              help='Файл для сохранения метрик')
    
    # Команда report
    report_parser = subparsers.add_parser('report', help='Генерация отчетов')
    report_parser.add_argument('-t', '--type', choices=['text', 'html', 'json'], 
                              default='text', help='Тип отчета')
    report_parser.add_argument('-f', '--file', default='metrics.json',
                              help='Файл с метриками')
    report_parser.add_argument('-o', '--output', help='Выходной файл')
    
    # Команда visualize
    viz_parser = subparsers.add_parser('visualize', help='Визуализация данных')
    viz_parser.add_argument('-t', '--type', required=True,
                          choices=['cpu', 'memory', 'disk', 'network', 'all'],
                          help='Тип графика')
    viz_parser.add_argument('-f', '--file', default='metrics.json',
                          help='Файл с метриками')
    viz_parser.add_argument('-o', '--output', help='Выходной файл')
    
    # Команда schedule
    schedule_parser = subparsers.add_parser('schedule', help='Планирование отчетов')
    schedule_parser.add_argument('frequency', choices=['hourly', 'daily', 'weekly'],
                               help='Частота отчетов')
    schedule_parser.add_argument('-c', '--continuous', action='store_true',
                               help='Непрерывный режим')
    
    return parser.parse_args()


def main():
    """Основная функция CLI"""
    args = parse_arguments()
    
    try:
        validate_config(DEFAULT_CONFIG)
        
        if args.command == 'collect':
            print(f"Сбор метрик ({args.count} измерений, интервал {args.interval} сек)...")
            collector = SystemMetricsCollector()
            metrics = collector.collect_continuous(args.count, args.interval)
            collector.save_metrics(metrics, args.output)
            print(f"Метрики сохранены в {args.output}")
            
        elif args.command == 'report':
            print(f"Генерация {args.type} отчета...")
            reporter = ReportGenerator()
            report = reporter.generate_report(args.file, args.type)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"Отчет сохранен в {args.output}")
            else:
                if args.type == 'text':
                    print(report)
                else:
                    print(f"Отчет сгенерирован ({len(report)} байт)")
                    
        elif args.command == 'visualize':
            print(f"Создание графика: {args.type}...")
            visualizer = MetricsVisualizer()
            output_file = visualizer.create_chart(args.file, args.type, args.output)
            print(f"График сохранен в {output_file}")
            
        elif args.command == 'schedule':
            print(f"Запуск планировщика ({args.frequency} отчеты)...")
            scheduler = ReportScheduler()
            if args.continuous:
                scheduler.run_continuous(args.frequency)
            else:
                scheduler.run_once(args.frequency)
                
        else:
            print("Используйте --help для просмотра доступных команд")
            sys.exit(1)
            
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


# Прямой запуск программы
main()
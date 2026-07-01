#!/usr/bin/env python3
import sys
import subprocess
import argparse
import csv

def get_installed_packages():
    """Вызываем dpkg-query и забираем текст из системы"""
    try:
        cmd = ["dpkg-query", "-W", "-f=${Package};${Version};${Architecture}\n"]
        result = subprocess.run(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check = True)
        package=[]
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(';')
                if len(parts) == 3:
                    package.append({
                        'name': parts[0],
                        'version': parts[1],
                        'arch': parts[2]
                    })
        return package
    except FileNotFoundError:
        print("Ошибка: Скрипт должен запускаться в среде Astra Linux / Debian.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка пакетного менеджера: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def print_table(packages,show_version_only=False):
    if not packages:
        print("Пакеты не найдены.")
        return
    if show_version_only:
        print(f"{'Название пакета':<40} | {'Версия':<30}")
        print('-' * 70)
        for p in packages:
            print(f"{p['name']:<40} | {p['version']:<30}")
    else:
        print(f"{'Название пакета':<40} | {'Версия':<30} | {'Архитектура':<10}")
        print("-" * 88)
        for p in packages:
            print(f"{p['name']:<40} | {p['version']:<30} | {p['arch']:<10}")


def export_to_csv(packages, filename):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            writer.writerow(['Package Name', 'Version', 'Architecture'])
            
            for p in packages:
                writer.writerow([p['name'], p['version'], p['arch']])
                
        print(f"Отчет успешно сохранен в файл: {filename}")
        
    except IOError as e:
        print(f"Ошибка записи в файл: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="software-inventory — утилита инвентаризации ПО для Astra Linux."
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='Показать все пакеты')
    group.add_argument('--search', metavar='<package>', type=str, help='Поиск по имени')
    group.add_argument('--arch', metavar='<architecture>', type=str, help='Фильтр по архитектуре')
    group.add_argument('--version-pkg', metavar='<package>', type=str, help='Вывод версии конкретного пакета')
    group.add_argument('--export', metavar='report.csv', type=str, help='Экспорт отчета в CSV')

    args = parser.parse_args()

    all_packages = get_installed_packages()

    if args.list:
        print_table(all_packages)
        
    elif args.search:
        filtered = [p for p in all_packages if args.search.lower() in p['name'].lower()]
        print_table(filtered)
        
    elif args.arch:
        filtered = [p for p in all_packages if p['arch'] == args.arch]
        print_table(filtered)
        
    elif args.version_pkg:
        filtered = [p for p in all_packages if args.version_pkg.lower() in p['name'].lower()]
        print_table(filtered, show_version_only=True)
        
    elif args.export:
        export_to_csv(all_packages, args.export)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма принудительно завершена пользователем.")
        sys.exit(0)
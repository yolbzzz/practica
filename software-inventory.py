#!/usr/bin/env python3
import sys
import subprocess
import argparse
import csv
# импорт всех нужных библиотек для работы с ОС, а также шебанг

def get_installed_packages():
    try:
        '''Функция получает список всех установленных в системе пакетов с помощью dpkg-query.
        Парсит её стандартный вывод и формирует список словарей с данными.'''

        # Формируем команду для dpkg-query.
        cmd = ["dpkg-query", "-W", "-f=${Package};${Version};${Architecture}\n"]
        # Запускаем команду и перенаправляем stdout и stderr, чтобы Python их перехватил.
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # Форматируем вывод
        packages = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(';')
                if len(parts) == 3:
                    packages.append({
                        'name': parts[0],
                        'version': parts[1],
                        'arch': parts[2]
                    })
        return packages
    # обработка ошибок
    except FileNotFoundError:
        print("Ошибка: Скрипт должен запускаться в среде Astra Linux / Debian.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка пакетного менеджера: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def print_table(packages):
    '''Выводит список пакетов в консоль в виде отформатированной текстовой таблицы.'''

    if not packages:
        print("Пакеты не найдены.")
        return
    print(f"{'Название пакета':<40} | {'Версия':<30} | {'Архитектура':<10}")
    print("-" * 88)
    for p in packages:
        print(f"{p['name']:<40} | {p['version']:<30} | {p['arch']:<10}")


def export_to_csv(packages, filename):
    '''Экспортирует переданный список пакетов в файл формата CSV.'''

    if not packages:
        print("Нет данных для экспорта.", file=sys.stderr)
        return
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Package Name', 'Version', 'Architecture'])
            for p in packages:
                writer.writerow([p['name'], p['version'], p['arch']])
        print(f"Отчет успешно сохранен в файл: {filename}")
    # Обработка ошибок ввода-вывода
    except IOError as e:
        print(f"Ошибка записи в файл: {e}", file=sys.stderr)


def main():
    '''Основная функция управления утилитой.'''

    # Инициализируем парсер аргументов командной строки, автоматически генерирует текст справки по параметру --help.
    parser = argparse.ArgumentParser(
        description="software-inventory — утилита инвентаризации ПО для Astra Linux."
    )
    
    # Основные режимы работы (взаимоисключающие)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='Показать все установленные пакеты')
    group.add_argument('--search', metavar='<package>', type=str, help='Поиск пакета по имени')
    group.add_argument('--arch', metavar='<architecture>', type=str, help='Фильтрация пакетов по архитектуре')
    # Пустой флаг для совместимости, если под экспортом "всего" без параметров понимался отдельный вызов
    group.add_argument('--export-all', metavar='<file.csv>', type=str, help='Экспортировать весь список в CSV')

    # Опциональный флаг для сохранения результатов фильтрации/поиска
    parser.add_argument('--export', metavar='<file.csv>', type=str, help='Экспорт отфильтрованного отчета в CSV')

    # Парсим переданные аргументы командной строки
    args = parser.parse_args()
    all_packages = get_installed_packages()
    filtered_packages = []

    # Отбор данных в зависимости от флага
    if args.list:
        filtered_packages = all_packages
    elif args.search:
        filtered_packages = [p for p in all_packages if args.search.lower() in p['name'].lower()]
    elif args.arch:
        filtered_packages = [p for p in all_packages if p['arch'] == args.arch]
    elif args.export_all:
        filtered_packages = all_packages
        args.export = args.export_all # Перенаправляем имя файла

    # Вывод или сохранение результата
    if args.export:
        export_to_csv(filtered_packages, args.export)
    else:
        print_table(filtered_packages)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # Завершение программы с помощью Ctlr+C
        print("\nПрограмма принудительно завершена пользователем.")
        sys.exit(0)
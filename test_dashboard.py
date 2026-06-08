#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности дашборда
"""

import sys

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("🔍 Проверка зависимостей...")

    required_packages = {
        'dash': '2.14.2',
        'pandas': '2.1.4',
        'plotly': '5.18.0',
        'dash_bootstrap_components': '1.5.0'
    }

    missing_packages = []

    for package, version in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - НЕ УСТАНОВЛЕН")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Установите отсутствующие пакеты:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False

    print("\n✅ Все зависимости установлены!\n")
    return True


def check_csv_file():
    """Проверка наличия CSV файла"""
    import os
    print("🔍 Проверка файла данных...")

    if os.path.exists('software_dev_data.csv'):
        print("  ✅ software_dev_data.csv найден\n")
        return True
    else:
        print("  ⚠️  software_dev_data.csv не найден")
        print("  Создайте файл или загрузите через веб-интерфейс\n")
        return True  # Не критично, можно загрузить через UI


def validate_app_structure():
    """Проверка структуры приложения"""
    import os
    print("🔍 Проверка структуры проекта...")

    required_files = ['app.py', 'requirements.txt', 'README.md']

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - НЕ НАЙДЕН")
            return False

    print("\n✅ Структура проекта корректна!\n")
    return True


def main():
    """Основная функция проверки"""
    print("=" * 60)
    print("  ПРОВЕРКА ДАШБОРДА: Процесс разработки ПО")
    print("=" * 60)
    print()

    checks = [
        check_dependencies(),
        check_csv_file(),
        validate_app_structure()
    ]

    print("=" * 60)
    if all(checks):
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\nЗапустите приложение:")
        print("  python app.py")
        print("\nПерейдите в браузере:")
        print("  http://127.0.0.1:8050")
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Исправьте ошибки и повторите проверку")
        sys.exit(1)
    print("=" * 60)


if __name__ == '__main__':
    main()

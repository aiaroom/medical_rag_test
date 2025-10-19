# run_tests.py
#!/usr/bin/env python3
"""
Запуск всех pytest тестов для медицинской системы
"""

import pytest
import sys
import os

def main():
    """Основная функция запуска тестов"""
    print("🚀 ЗАПУСК ВСЕХ PYTEST ТЕСТОВ")
    print("=" * 60)
    
    # Аргументы для pytest
    pytest_args = [
        "tests/",           # Папка с тестами
        "-v",               # Подробный вывод
        "--tb=short",       # Короткий traceback
        "--durations=10",   # Показать 10 самых медленных тестов
    ]
    
    # Добавляем маркеры для выборочного запуска
    if len(sys.argv) > 1:
        if sys.argv[1] == "fast":
            pytest_args.extend(["-m", "not slow"])
            print("⚡ Запуск только быстрых тестов")
        elif sys.argv[1] == "slow":
            pytest_args.extend(["-m", "slow"])
            print("🐌 Запуск только медленных тестов")
        elif sys.argv[1] == "performance":
            pytest_args.extend(["-m", "performance"])
            print("⏱️  Запуск тестов производительности")
    
    # Запускаем pytest
    exit_code = pytest.main(pytest_args)
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
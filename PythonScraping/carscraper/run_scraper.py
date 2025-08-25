import subprocess
import sys
import datetime
import os


def run_spider(spider_name="carspider"):
    """Запуск Scrapy spider через subprocess"""

    # Генеруємо timestamp для унікальних файлів
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Визначаємо правильний шлях до Python
    if os.name == 'nt':  # Windows
        # Пробуємо знайти venv в різних місцях
        possible_paths = [
            os.path.join('.venv', 'Scripts', 'python.exe'),
            os.path.join('..', '.venv', 'Scripts', 'python.exe'),
            os.path.join('venv', 'Scripts', 'python.exe'),
            sys.executable  # Fallback - поточний Python
        ]

        python_exec = None
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                python_exec = full_path
                break

        if not python_exec:
            python_exec = sys.executable
            print(f"⚠️  Використовується системний Python: {python_exec}")
        else:
            print(f"✅ Знайдено Python: {python_exec}")
    else:
        python_exec = sys.executable

    # Перевіряємо чи ми в правильному каталозі (має бути scrapy.cfg)
    scrapy_cfg = 'scrapy.cfg'
    if not os.path.exists(scrapy_cfg):
        print(f"❌ scrapy.cfg не знайдено в {os.path.abspath('carscraper')}")
        print("Запустіть скрипт з кореневого каталогу проекту!")
        return False

    # Створюємо необхідні папки
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    # Змінюємо робочий каталог на carscraper (де scrapy.cfg)
    original_dir = os.getcwd()
    scrapy_dir = os.path.abspath('carscraper')
    os.chdir(scrapy_dir)

    try:
        # Формуємо команду для запуску
        log_file = os.path.join('..', 'logs', f'spider_{timestamp}.log')
        data_file = os.path.join('..', 'data', f'cars_{timestamp}.csv')

        cmd = [
            python_exec, '-m', 'scrapy', 'crawl', spider_name,
            '-L', 'INFO',
            '--logfile', log_file,
            '-o', data_file
        ]

        print(f"🚀 Запуск команди: {' '.join(cmd)}")
        print(f"📁 Робочий каталог: {os.getcwd()}")

        # Запускаємо spider
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=scrapy_dir
        )

        print(f"✅ Spider '{spider_name}' завершився успішно (код: {result.returncode})")
        print(f"📄 Лог файл: {os.path.abspath(log_file)}")
        print(f"📊 Файл даних: {os.path.abspath(data_file)}")

        if result.stdout:
            print("📤 Stdout:", result.stdout[:500])

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка запуску spider: {e}")
        print(f"📤 Stdout: {e.stdout}")
        print(f"📥 Stderr: {e.stderr}")
        return False

    except FileNotFoundError as e:
        print(f"❌ Файл не знайдено: {e}")
        print(f"🔍 Перевірте шлях до Python: {python_exec}")
        return False

    finally:
        # Повертаємося в оригінальний каталог
        os.chdir(original_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run scrapy spider from CLI")
    parser.add_argument('--spider', default="carspider", help='Spider name to run')
    args = parser.parse_args()

    success = run_spider(args.spider)
    sys.exit(0 if success else 1)
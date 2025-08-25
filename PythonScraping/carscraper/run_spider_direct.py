# run_spider_direct.py
import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    # Отримуємо поточний каталог (має бути корінь проекту)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    carscraper_dir = os.path.join(current_dir, 'carscraper')

    # Перевіряємо чи існує каталог carscraper
    if not os.path.exists(carscraper_dir):
        print(f"Каталог carscraper не знайдено: {carscraper_dir}")
        print("Запустіть скрипт з кореневого каталогу проекту!")
        return

    # Змінюємо робочий каталог
    os.chdir(carscraper_dir)
    print(f"✅ Змінено робочий каталог на: {os.getcwd()}")

    # Створюємо папку logs якщо не існує
    logs_dir = os.path.join(carscraper_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    print(f"✅ Папка logs створена: {logs_dir}")

    # Додаємо шлях до проекту в PYTHONPATH
    sys.path.insert(0, carscraper_dir)

    try:
        # Отримуємо налаштування проекту
        settings = get_project_settings()

        # Додаткові налаштування для локального запуску
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('LOG_FILE', os.path.join(logs_dir, 'spider_local.log'))
        settings.set('LOG_ENABLED', True)
        settings.set('LOG_ENCODING', 'utf-8')

        # Виводимо інформацію
        print(f"Лог файл: {settings.get('LOG_FILE')}")
        print(f"Рівень логування: {settings.get('LOG_LEVEL')}")

        # Створюємо процес
        process = CrawlerProcess(settings)

        # Додаємо spider
        process.crawl('carspider')

        print("Запуск spider...")

        # Запускаємо
        process.start()

    except Exception as e:
        print(f"Помилка при запуску spider: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
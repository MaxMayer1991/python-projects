# test_spider.py
import os
import sys
from scrapy import cmdline


def test_spider():
    """Тестує spider без повного запуску"""
    os.chdir('carscraper')

    # Тестування налаштувань
    cmdline.execute(['scrapy', 'check', 'carspider'])

    # Тестування парсингу
    cmdline.execute(['scrapy', 'parse',
                     '--spider=carspider',
                     'https://auto.ria.com/uk/car/used/',
                     '--callback=parse'])


if __name__ == '__main__':
    test_spider()

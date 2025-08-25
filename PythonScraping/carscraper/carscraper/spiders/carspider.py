import scrapy
import re
import os
import time
import logging
from datetime import datetime
from queue import Queue
from threading import Lock
from itemloaders.processors import MapCompose
from ..items import CarItem
from scrapy.loader import ItemLoader
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class CarspiderSpider(scrapy.Spider):
    name = "carspider"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    def __init__(self, *args, **kwargs):
        super(CarspiderSpider, self).__init__(*args, **kwargs)
        self.logger.info("Starting the Carspider Spider")

        # === НАЛАШТУВАННЯ ПУЛУ ДРАЙВЕРІВ ===
        self.driver_pool = Queue()
        self.pool_lock = Lock()
        self.pool_size = 3  # Кількість драйверів у пулі

        # Створюємо пул драйверів з оптимізованими налаштуваннями
        self._create_driver_pool()

    def _get_optimized_chrome_options(self):
        """Повертає оптимізовані опції Chrome для швидкості"""
        chrome_options = Options()

        # === ОСНОВНІ НАЛАШТУВАННЯ ШВИДКОСТІ ===
        chrome_options.add_argument("--headless")  # Без GUI
        chrome_options.add_argument("--no-sandbox")  # Швидкість + безпека
        chrome_options.add_argument("--disable-dev-shm-usage")  # RAM оптимізація

        # === ВІДКЛЮЧЕННЯ GPU (усуває помилки) ===
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")

        # === ШВИДКІСТЬ ЗАВАНТАЖЕННЯ ===
        chrome_options.add_argument("--disable-images")  # Не завантажувати зображення
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")

        # === ВІДКЛЮЧЕННЯ НЕПОТРІБНИХ ФУНКЦІЙ (усуває помилки) ===
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-background-networking")

        # === ВІДКЛЮЧЕННЯ GCM/SYNC (усуває PHONE_REGISTRATION_ERROR) ===
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--disable-background-mode")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")

        # === ВІДКЛЮЧЕННЯ WEBGL (усуває WebGL помилки) ===
        chrome_options.add_argument("--disable-webgl")
        chrome_options.add_argument("--disable-webgl2")
        chrome_options.add_argument("--disable-3d-apis")

        # === ЛОГУВАННЯ (усуває DevTools повідомлення) ===
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--log-level=3")  # Тільки FATAL помилки
        chrome_options.add_argument("--silent")

        # === PERFORMANCE ===
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")

        # === ДОДАТКОВІ НАЛАШТУВАННЯ ===
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--disable-features=TranslateUI")

        return chrome_options

    def _create_single_driver(self):
        """Створює один драйвер з оптимізованими налаштуваннями"""
        chrome_options = self._get_optimized_chrome_options()

        # Налаштування логування для Selenium
        selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        selenium_logger.setLevel(logging.WARNING)

        try:
            driver = webdriver.Chrome(options=chrome_options)

            # === ДОДАТКОВІ НАЛАШТУВАННЯ DRIVER ===
            driver.set_page_load_timeout(30)  # Timeout для сторінок
            driver.implicitly_wait(10)  # Неявне очікування елементів

            self.logger.info("✅ Chrome driver created successfully")
            return driver

        except Exception as e:
            self.logger.error(f"❌ Failed to create Chrome driver: {e}")
            return None

    def _create_driver_pool(self):
        """Створює пул драйверів"""
        self.logger.info(f"Creating driver pool with {self.pool_size} drivers...")

        successful_drivers = 0
        for i in range(self.pool_size):
            driver = self._create_single_driver()
            if driver:
                self.driver_pool.put(driver)
                successful_drivers += 1
                self.logger.info(f"Driver {i + 1}/{self.pool_size} added to pool")
            else:
                self.logger.error(f"Failed to create driver {i + 1}/{self.pool_size}")

        if successful_drivers == 0:
            raise Exception("❌ Failed to create any drivers! Cannot continue.")

        self.logger.info(f"✅ Driver pool created with {successful_drivers} drivers")

    def get_driver(self):
        """Отримує драйвер з пулу"""
        with self.pool_lock:
            if not self.driver_pool.empty():
                driver = self.driver_pool.get()
                self.logger.debug("Got driver from pool")
                return driver
            else:
                # Якщо пул порожній, створюємо новий драйвер
                self.logger.warning("Pool is empty, creating new driver")
                return self._create_single_driver()

    def return_driver(self, driver):
        """Повертає драйвер в пул"""
        if driver:
            with self.pool_lock:
                self.driver_pool.put(driver)
                self.logger.debug("Returned driver to pool")

    def parse(self, response):
        """Парсинг головної сторінки зі списком автомобілів"""
        self.logger.info(f'Parsing page: {response.url}')

        # Знаходимо всі автомобілі на сторінці
        cars = response.css('section.ticket-item')
        self.logger.info(f'Found {len(cars)} cars on page')

        for car in cars:
            # Отримуємо URL автомобіля
            car_url = car.css('a.m-link-ticket::attr(href), a.address::attr(href)').get()

            if car_url is not None:
                self.logger.info(f'Processing car URL: {car_url}')

                # Пропускаємо нові автомобілі
                if 'newauto' in car_url.lower():
                    self.logger.info(f'Detected NEW car: {car_url}, skipping...')
                    continue
                else:
                    self.logger.info(f'Used car: {car_url}')
                    yield response.follow(car_url, callback=self.parse_car_page)

        # Пагінація - переходимо на наступну сторінку
        next_page = response.css('a.js-next.page-link::attr(href), a.page-link.js-next::attr(href)').get()
        if next_page:
            self.logger.info(f'Found next page: {next_page}')
            yield response.follow(next_page, callback=self.parse)
        else:
            self.logger.info('No more pages found')

    def parse_car_page(self, response):
        """Обробка сторінки автомобіля з використанням пулу драйверів"""
        driver = self.get_driver()

        if not driver:
            self.logger.error("❌ No driver available, skipping page")
            return

        try:
            driver.get(response.url)
            self.logger.info(f"=== PROCESSING: {response.url} ===")

            # --- Обробка Cookie банера ---
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-cta-do-not-consent"))
                )
                cookie_button.click()
                self.logger.info("Cookie banner closed")
            except TimeoutException:
                self.logger.debug("Cookie banner not found")

            # --- Витягування телефону ---
            phone_number = self.extract_phone_number(driver)

            # --- Збір даних ---
            prices_raw = response.css(
                'div.price_value strong::text, div.price_value--additional span.i-block span::text'
            ).getall()
            self.logger.info(f"Debug price_usd raw values: {prices_raw}")

            loader = ItemLoader(item=CarItem(), response=response)
            loader.add_value('url', response.url)
            loader.add_css('title', 'h1.head::text')
            loader.add_css('price_usd',
                           'div.price_value strong::text, div.price_value--additional span.i-block span::text')
            loader.add_css('odometer', 'div.base-information span.size18::text')
            loader.add_css('username',
                           'div.seller_info_name.bold a.sellerPro::text, h4.seller_info_name a::text, div.seller_info_name::text')
            loader.add_value('phone_number', phone_number)
            loader.add_css('image_url', 'div.photo-620x465 picture img::attr(src)')
            loader.add_css('image_count', 'span.count span.mhide::text')
            loader.add_css('car_number', 'span.state-num::text')
            loader.add_css('car_vin', 'span.label-vin::text, div.t-check span.vin-code::text')

            yield loader.load_item()

        except Exception as e:
            self.logger.error(f"Error processing page {response.url}: {e}")
        finally:
            # ЗАВЖДИ повертаємо драйвер в пул
            self.return_driver(driver)

    def extract_phone_number(self, driver):
        """Витягуємо номер телефону (отримує driver як параметр)"""
        self.logger.info("=== STARTING PHONE EXTRACTION ===")
        # Метод 1: Витягування номеру телефону після кліку
        phone = self.extract_phone_with_click(driver)
        self.logger.info(f"extract_phone_with_click returned: {phone}")
        if phone:
            return phone

        # Метод 2: Витягуємо з тексту сторінки
        phone = self.extract_phone_from_text(driver)
        self.logger.info(f"extract_phone_from_text returned: {phone}")
        if phone:
            return phone

        self.logger.warning("=== NO PHONE FOUND - RETURNING EMPTY ===")
        return []  # ✅ Повертаємо пустий список

    def extract_phone_from_text(self, driver):
        """Витягуємо телефон з тексту сторінки"""
        try:
            # Чекаємо завантаження JS
            time.sleep(3)

            page_source = driver.page_source
            self.logger.info(f"Page source length: {len(page_source)}")

            # Розширені патерни для телефонів
            phone_patterns = [
                r'\(0(\d{2})\)\s*(\d{3})\s*(\d{2})\s*(\d{2})',  # (067) 123 45 67
                r'\+38\s*\(0(\d{2})\)\s*(\d{3})\s*(\d{2})\s*(\d{2})',  # +38 (067) 123 45 67
                r'\+380(\d{2})(\d{3})(\d{2})(\d{2})',  # +380671234567
                r'380(\d{2})(\d{3})(\d{2})(\d{2})',  # 380671234567
                r'0(\d{2})(\d{3})(\d{2})(\d{2})',  # 0671234567
            ]

            for i, pattern in enumerate(phone_patterns):
                matches = re.findall(pattern, page_source)
                self.logger.info(f"Pattern {i + 1} found {len(matches)} matches")

                if matches:
                    match = matches[0]
                    if len(match) == 4:  # (067) 123 45 67 формат
                        phone_digits = ''.join(match)
                        if len(phone_digits) == 9:
                            formatted_phone = f"+380{phone_digits}"
                        else:
                            formatted_phone = f"+38{phone_digits}"
                    else:
                        phone_digits = ''.join(match)
                        formatted_phone = f"+380{phone_digits}"

                    self.logger.info(f"Phone extracted from text: {formatted_phone}")
                    return [formatted_phone]

            self.logger.info("No phone patterns matched")
            return None

        except Exception as e:
            self.logger.error(f"Error extracting phone from text: {e}")
            return None

    def extract_phone_with_click(self, driver):
        """Пробуємо клікнути кнопку показу телефону"""
        try:
            # Різні селектори для кнопки показу телефону
            button_selectors = [
                'div#phonesBlock .link-dotted',
                'a.toggle-phone-number-button',
                '.show-phone-button',
                'button[onclick*="phone"]',
                '.phone-reveal',
                '[data-toggle="phone"]'
            ]

            for selector in button_selectors:
                try:
                    button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )

                    # Клікаємо через JavaScript
                    driver.execute_script("arguments[0].click();", button)
                    self.logger.info(f"Clicked phone button: {selector}")

                    # Чекаємо появи телефону
                    time.sleep(2)

                    # Пробуємо знайти телефон після кліку
                    phone_after_click = self.find_phone_after_click(driver)
                    if phone_after_click:
                        self.logger.info(f"Found phone after click: {phone_after_click}")
                        return phone_after_click

                except TimeoutException:
                    continue
                except Exception as e:
                    self.logger.warning(f"Failed to click {selector}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in extract_phone_with_click: {e}")

        return None

    def find_phone_after_click(self, driver):
        """Шукаємо телефон після кліку на кнопку"""
        try:
            phone_selectors = [
                'a[href^="tel:"]',
                '#phonesBlock a',
                '.popup-successful-call a',
                '.phone-popup a',
                '[class*="phone-number"]'
            ]

            for selector in phone_selectors:
                try:
                    elements = WebDriverWait(driver, 3).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )

                    phone_numbers = []
                    for element in elements:
                        text = element.text.strip()
                        href = element.get_attribute('href')

                        if text and len(text) > 5:
                            phone_numbers.append(text)
                        elif href and 'tel:' in href:
                            phone_numbers.append(href.replace('tel:', ''))

                    if phone_numbers:
                        self.logger.info(f"Found phones after click: {phone_numbers}")
                        return phone_numbers

                except TimeoutException:
                    continue

        except Exception as e:
            self.logger.error(f"Error finding phone after click: {e}")

        return None

    def close(self, reason):
        """Закриваємо всі драйвери при завершенні"""
        try:
            self.logger.info("Closing driver pool...")

            # Закриваємо всі драйвери в пулі
            while not self.driver_pool.empty():
                try:
                    driver = self.driver_pool.get_nowait()
                    driver.quit()
                    self.logger.info("Driver closed")
                except:
                    pass

            self.logger.info("✅ All drivers closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing drivers: {e}")
        # ✅ НЕ викликаємо super().close(reason) - цього методу не існує!

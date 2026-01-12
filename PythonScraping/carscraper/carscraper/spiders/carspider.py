import scrapy
from ..items import CarItem
from scrapy.loader import ItemLoader
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError


class CarspiderSpider(scrapy.Spider):
    name = "carspider"
    allowed_domains = ["auto.ria.com"]
    # Використовуємо start_urls, Scrapy сам викличе start_requests
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    async def parse(self, response):
        """Парсинг сторінки лістингу (без Playwright)"""
        self.logger.info(f'Parsing page: {response.url}')

        # Знаходимо всі автомобілі
        cars = response.css('section.ticket-item')

        for car in cars:
            car_url = car.css('a.m-link-ticket::attr(href), a.address::attr(href)').get()

            if car_url:
                if 'newauto' in car_url.lower():
                    continue

                # Вмикаємо Playwright для сторінки авто
                yield response.follow(
                    car_url,
                    callback=self.parse_car_page,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'playwright_context': 'default',
                    }
                )

        # Пагінація
        next_page = response.css('a.js-next.page-link::attr(href), a.page-link.js-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    async def parse_car_page(self, response):
        """Асинхронна обробка сторінки авто через Playwright"""
        page: Page = response.meta.get('playwright_page')

        if not page:
            self.logger.error(f"Failed to get Playwright page for {response.url}")
            return

        try:
            self.logger.info(f"PROCESSING: {response.url}")

            # 1. Швидка перевірка Cookie банера
            # Використовуємо селектор, який точно вказує на кнопку
            cookie_selector = "button.fc-cta-do-not-consent"
            try:
                # Перевіряємо видимість без очікування (або з мінімальним)
                if await page.is_visible(cookie_selector, timeout=1000):
                    await page.click(cookie_selector, force=True)
                    self.logger.info("Cookie banner closed")
            except Exception:
                pass  # Ігноруємо будь-які помилки з банером, це не критично

            # 2. Клік по телефону
            phone_number = []
            phone_btn_selectors = [
                'div#phonesBlock .link-dotted',
                '[data-toggle="phone"]',
                '.show-phone-button'
            ]

            clicked = False
            for selector in phone_btn_selectors:
                try:
                    if await page.is_visible(selector, timeout=500):
                        await page.click(selector, timeout=2000, force=True)
                        clicked = True
                        self.logger.info(f"Clicked phone button: {selector}")
                        break
                except Exception:
                    continue

            if clicked:
                try:
                    # Чекаємо появи номера (popup або зміни тексту)
                    await page.wait_for_selector('.popup-successful-call, .phone-popup, [class*="phone-number"]',
                                                 timeout=2000)
                except PlaywrightTimeoutError:
                    pass

                # Оновлюємо контент
                content = await page.content()
                from scrapy.selector import Selector
                sel = Selector(text=content)

                phones = sel.css(
                    'div.popup-successful-call a::text, .phone-popup a::text, a[href^="tel:"]::text').getall()
                phone_number = [p.strip() for p in phones if len(p.strip()) > 5]

            # Fallback regex, якщо клік не спрацював
            if not phone_number:
                import re
                text_content = await page.inner_text('body', timeout=2000)  # Таймаут щоб не висіло
                patterns = [
                    r'\+38\s*\(0\d{2}\)\s*\d{3}\s*\d{2}\s*\d{2}',
                    r'0\d{2}\s*\d{3}\s*\d{2}\s*\d{2}'
                ]
                for p in patterns:
                    matches = re.findall(p, text_content)
                    if matches:
                        phone_number.extend(matches)
                        break

            # 3. Збір даних
            final_content = await page.content()
            from scrapy.selector import Selector
            final_selector = Selector(text=final_content)
            # Стабільні селектори
            loader = ItemLoader(item=CarItem(), selector=final_selector)
            loader.add_value('url', response.url)
            loader.add_css('title', 'div#sideTitleTitle span::text')
            loader.add_css('price_usd',
                           'div#sidePrice strong::text, div.price_value--additional span.i-block span::text')
            loader.add_css('odometer', 'div#basicInfoTableMainInfo0 span::text')
            loader.add_css('username',
                           'div#sellerInfoUserName span::text, h4.seller_info_name a::text, div.seller_info_name::text')
            loader.add_value('phone_number', phone_number)
            loader.add_css('image_url', 'img::attr(data-src), .gallery-order img::attr(src)')
            loader.add_css('image_count', 'div#photoSlider span + span::text')
            loader.add_css('car_number', 'div.car-number span::text')
            loader.add_css('car_vin', 'span#badgesVin span::text, div.t-check span.vin-code::text')

            yield loader.load_item()

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            # БЕЗПЕЧНЕ закриття сторінки
            try:
                if page and not page.is_closed():
                    await page.close()
            except Exception:
                # Якщо з'єднання вже розірвано (Connection closed), просто ігноруємо
                pass
from playwright.async_api import Page
from requests import Response
from scrapy.loader import ItemLoader
from scraper_autoria.scraper_autoria.items import ScraperAutoriaItem
import os, re, sys, asyncio, scrapy
from scrapy.selector import Selector
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class AutoriaSpider(scrapy.Spider):
    name = "autoria"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'playwright': True, 'proxy': os.getenv('PROXY_URL')})

    def parse(self, response, **kwargs):
        cars = response.css('section.ticket-item')

        for car in cars:
            car_url = car.css('a.m-link-ticket::attr(href), a.address::attr(href)').get()

            if car_url and not car_url.strip().startswith(('javascript', '#')):
                if 'newauto' in car_url.lower():
                    continue

                # Вмикаємо Playwright для сторінки авто
                yield response.follow(
                    car_url,
                    callback=self.parse_car_page,
                    meta={
                        'playwright': True,
                        'playwright_include_page': True,
                        'playwright_context': 'new',

                        # 👇 ВАЖЛИВО: Не чекати повного 'load', достатньо DOM
                        'playwright_page_goto_kwargs': {
                            'wait_until': 'domcontentloaded',
                            'timeout': 60000,  # Збільшимо таймаут до 60с для проксі
                        },


                    }
                )

            # Пагінація
        next_page = response.css('a.js-next.page-link::attr(href), a.page-link.js-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

#     async def parse_car_page(self, response):
#         page: Page = response.meta.get('playwright_page')
#         if not page:
#             return
#
#         try:
#             self.logger.info(f"PROCESSING: {response.url}")
#             page.set_default_timeout(5000)
#             # 1. ЧЕКАЄМО ЗАВАНТАЖЕННЯ (React версія)
#             try:
#                 # Чекаємо тільки критичні елементи
#                 await page.wait_for_selector('div.price_value', timeout=10000)
#             except Exception:
#                 self.logger.warning(f"⚠️ Load timeout: {response.url}")
#                 await page.close()
#                 return
#
#             # 2. COOKIE BANNER
#             try:
#                 if await page.is_visible("button.fc-cta-do-not-consent", timeout=2000):
#                     await page.click("button.fc-cta-do-not-consent", force=True)
#                     await page.locator("button.fc-cta-do-not-consent").click(force=True)
#                     #fc-button fc-cta-do-not-consent fc-secondary-button
#                     self.logger.info("✅ Cookie banner clicked")
#             except Exception:
#                 pass
#
#             # 3. КЛІК ПО ТЕЛЕФОНУ
#             # Селектор з вашого тесту, який точно працює
#             phone_number = []
#             btn_selector = 'button.size-large.conversion[data-action="showBottomPopUp"]'
#             try:
#                 # Locator ледачий, він не чекає поки елемент з'явиться, поки ми його не попросимо
#                 btn = page.locator(btn_selector).first
#
#                 if await btn.is_visible():  # Швидка перевірка
#                     # Скрол часто не потрібен, якщо headless, але для надійності залишимо
#                     await btn.scroll_into_view_if_needed()
#                     await btn.click(force=True)
#                     self.logger.info("✅ Clicked")
#
#                     # 4. Очікування даних (Smart Wait)
#                     # Чекаємо поки з'явиться або посилання tel, або текст кнопки зміниться на цифри
#                     # Це швидше за wait_for_timeout(1500), бо спрацює миттєво, як тільки дані прийдуть
#                     try:
#                         await page.wait_for_function("""
#                                         () => {
#                                             return document.querySelector('a[href^="tel:"]') ||
#                                                    /\d{3}/.test(document.querySelector('button[data-action="showBottomPopUp"]')?.innerText);
#                                         }
#                                     """, timeout=3000)  # Чекаємо макс 3 сек на появу номера
#                     except:
#                         pass  # Якщо не з'явився за 3 сек - забираємо що є
#             except Exception:
#                 pass  # Кнопки немає або помилка кліку
#             # clicked = False
#             # try:
#             #     # Чекаємо кнопку
#             #     await page.wait_for_selector(btn_selector, timeout=5000)
#             #     btn = page.locator(btn_selector).first
#             #
#             #     if await btn.count() > 0:
#             #         self.logger.info(f"🔎 Found button")
#             #         await btn.scroll_into_view_if_needed()
#             #         await page.wait_for_timeout(500)
#             #
#             #         # У Firefox нативний клік працює добре
#             #         await btn.click(force=True)
#             #         clicked = True
#             #         self.logger.info("✅ Clicked successfully")
#             #
#             #         # Даємо час на появу даних (1.5 сек)
#             #         await page.wait_for_timeout(1500)
#             # except Exception as e:
#             #     self.logger.warning(f"Click failed: {e}")
#             # # 4. ОТРИМАННЯ НОМЕРА (Логіка з playwright-test.py)
#             #
#             # if clicked:
#             #     try:
#             #         # У вашому тесті ви берете текст з div.popup-inner ... span
#             #         target_selector = 'div.popup-inner button.size-large.conversion span'
#             #         self.logger.info(f"📞 Found target selector: {target_selector}")
#             #         # Чекаємо поки з'явиться текст (номер)
#             #         await page.wait_for_selector(target_selector, timeout=5000)
#             #
#             #         # Отримуємо текст
#             #         extracted_text = await page.inner_text(target_selector)
#             #         self.logger.info(f"📞 Raw text from button: {extracted_text}")
#             #
#             #         # Чистимо номер
#             #         import re
#             #         # Шукаємо (063) 123 45 67
#             #         matches = re.findall(r'\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}', extracted_text)
#             #         if matches:
#             #             # Форматуємо: (063) 123 45 67 -> 380631234567
#             #             clean_num = '38' + re.sub(r'\D', '', matches[0])
#             #             phone_number.append(clean_num)
#             #         else:
#             #             # Якщо формат інший, просто чистимо все крім цифр
#             #             clean_num = re.sub(r'\D', '', extracted_text)
#             #             if len(clean_num) >= 10:
#             #                 phone_number.append(clean_num)
#             #
#             #     except Exception as e:
#             #         self.logger.warning(f"Text extraction failed: {e}")
#
#
#
#             # 4. ЗБІР ДАНИХ (Оновлюємо контент після кліків)
#             content = await page.content()
#             from scrapy.selector import Selector
#             sel = Selector(text=content)
#             hrefs = sel.css('a[href^="tel:"]::attr(href)').getall()
#             import re
#             #         # Шукаємо (063) 123 45 67
#             #         matches = re.findall(r'\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}', hrefs)
#             #         if matches:
#             #             # Форматуємо: (063) 123 45 67 -> 380631234567
#             #             clean_num = '38' + re.sub(r'\D', '', matches[0])
#             #             phone_number.append(clean_num)
#             #         else:
#             #             # Якщо формат інший, просто чистимо все крім цифр
#             #             clean_num = re.sub(r'\D', '', extracted_text)
#             #             if len(clean_num) >= 10:
#             #                 phone_number.append(clean_num)
#             if not phone_number:
#                 # Regex по всьому тексту (швидкий fallback)
#                 text = sel.get()
#             # # --- ЛОГУВАННЯ СИРИХ ДАНИХ (Щоб бачити, що знаходить CSS) ---
#             # raw_title = sel.css('div#basicInfoTitle h1::text, div#sideTitleTitle span::text').get()
#             # raw_price = sel.css(
#             #     'div#basicInfoPrice strong::text, div#sidePrice strong::text').getall()
#             # raw_odo = sel.css('div#basicInfoTableMainInfo0 span::text').get()
#             # raw_user = sel.css('div#sellerInfoUserName span::text').get()
#             # raw_img_url = sel.css('img::attr(data-src)').get()
#             # raw_img_count = sel.css('span.common-badge.alpha.medium span::text').get()
#             # raw_car_num = sel.css('div.car-number span::text').get()
#             # raw_car_vin = sel.css('span#badgesVin span::text').get()
#
#             # print(f"🔍 RAW DEBUG for {response.url}:")
#             # print(f"   Title: {raw_title}")
#             # print(f"   Price: {raw_price}")
#             # print(f"   Odometer: {raw_odo}")
#             # print(f"   Username: {raw_user}")
#             # print(f"   Phone number: {phone_number}")
#             # print(f"   Image url: {raw_img_url}")
#             # print(f"   Image count: {raw_img_count}")
#             # print(f"   Car number: {raw_car_num}")
#             # print(f"   VIN number: {raw_car_vin}")
# #-----------------------------------------------------------------------------------------------
#             # 5. ЗБІР ДАНИХ (Оновлені селектори під React)
#             final_content = await page.content()
#             from scrapy.selector import Selector
#             final_selector = Selector(text=final_content)
#
#             loader = ItemLoader(item=ScraperAutoriaItem(), selector=final_selector)
#             loader.add_value('url', response.url)
#
#             # Заголовок (autoPhoneTitle з вашого скріншоту або звичайний h1)
#             loader.add_css('title', 'div#basicInfoTitle h1::text, div#sideTitleTitle span::text')
#
#             # Ціна (React версія часто використовує strong.common-text)
#             loader.add_css('price_usd',
#                            'div#basicInfoPrice strong::text, div#sidePrice strong::text')
#             # Пробіг
#             loader.add_css('odometer', 'div#basicInfoTableMainInfo0 span::text')
#
#             # Ім'я продавця (з вашого скріншоту div#sellerInfo)
#             loader.add_css('username',
#                            'div#sellerInfoUserName span::text')
#
#             loader.add_value('phone_number', phone_number)  # set для унікальності
#             # Фото
#             loader.add_css('image_url', 'img::attr(data-src)')
#             # Кількість фото (використовуємо ваш TakeSecond логіку)
#             loader.add_css('image_count', 'span.common-badge.alpha.medium span::text')
#             loader.add_css('car_number', 'div.car-number span::text')
#             loader.add_css('car_vin', 'span#badgesVin span::text')
#
#             yield loader.load_item()
#
#         except Exception as e:
#             self.logger.error(f"Error processing {response.url}: {e}")
#         finally:
#             try:
#                 if page and not page.is_closed():
#                     await page.close()
#             except Exception:
#                 pass
    async def parse_car_page(self, response):
        page: Page = response.meta.get('playwright_page')
        if not page:
            return

        try:
            self.logger.info(f"PROCESSING: {response.url}")
            page.set_default_timeout(30000)

            # 5. ЗБІР ДАНИХ (Гібридний підхід)
            loader = ItemLoader(item=ScraperAutoriaItem(), response=response)
            loader.add_value('url', response.url)
            # Ваші стандартні селектори

            # 1. Швидка перевірка завантаження
            try:
                # 2. Cookie
                try:
                    cookie_selector = "button.fc-cta-do-not-consent"
                    await page.wait_for_selector(cookie_selector, timeout=3000)
                    await page.click(cookie_selector, force=True)
                    self.logger.info("✅ Cookie banner handled")
                    await asyncio.sleep(1)  # Small delay after cookie click
                except Exception:
                    pass

                await page.wait_for_selector('div#sellerInfo', state='attached', timeout=15000)
                # Collect all static data
                content = await page.content()
                sel = Selector(text=content)

                loader.add_css('title', 'div#basicInfoTitle h1::text, div#sideTitleTitle span::text')
                loader.add_css('price_usd', 'div#basicInfoPrice strong::text, div#sidePrice strong::text')
                loader.add_css('odometer', 'div#basicInfoTableMainInfo0 span::text')
                loader.add_css('username', 'div#sellerInfoUserName span::text')
                loader.add_css('image_url', 'img::attr(data-src)')
                loader.add_css('image_count', 'span.common-badge.alpha.medium span::text')
                loader.add_css('car_number', 'div.car-number span::text')
                loader.add_css('car_vin', 'span#badgesVin span::text')

            except Exception as e:
                self.logger.warning(f"Error collecting static data: {e}")




            # 3. КЛІК ПО ТЕЛЕФОНУ
            # Ми натискаємо ТІЛЬКИ ПЕРШУ кнопку. Цього достатньо, щоб отримати хоча б 1 номер.


            # try:
            #     # Locator ледачий, він не чекає поки елемент з'явиться, поки ми його не попросимо
            #     btn = page.locator(btn_selector).first
            #     if await btn.is_visible():  # Швидка перевірка
            #         # Скрол часто не потрібен, якщо headless, але для надійності залишимо
            #         await btn.scroll_into_view_if_needed()
            #         await btn.click(force=True)
            #         self.logger.info("✅ Clicked")
            #         # 4. Очікування даних (Smart Wait)
            #         # Чекаємо поки з'явиться або посилання tel, або текст кнопки зміниться на цифри
            #         # Це швидше за wait_for_timeout(1500), бо спрацює миттєво, як тільки дані прийдуть
            #         try:
            #             await page.wait_for_function("""
            #                             () => {
            #                                 return document.querySelector('a[href^="tel:"]') ||
            #                                        /\d{3}/.test(document.querySelector('button[data-action="showBottomPopUp"]')?.innerText);
            #                             }
            #                         """, timeout=3000)  # Чекаємо макс 3 сек на появу номера
            #         except:
            #             pass  # Якщо не з'явився за 3 сек - забираємо що є
            # except Exception:
            #     pass  # Кнопки немає або помилка кліку
            # clicked = False


                # if await btn.count() > 0:
                #         self.logger.info(f"🔎 Found button")
                #         await btn.scroll_into_view_if_needed()
                #         await page.wait_for_timeout(500)
                #
                #         # У Firefox нативний клік працює добре
                #         await btn.click(force=True)
                #         clicked = True
                #         self.logger.info("✅ Clicked successfully")
                #
                #         # Даємо час на появу даних (1.5 сек)
                #         await page.wait_for_timeout(1500)

                # # 4. ОТРИМАННЯ НОМЕРА (Логіка з playwright-test.py)

            # if clicked:


                    # # Чистимо номер
                    # import re
                    # # Шукаємо (063) 123 45 67
                    # matches = re.findall(r'\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}', extracted_text)
                    # if matches:
                    #     # Форматуємо: (063) 123 45 67 -> 380631234567
                    #     clean_num = '38' + re.sub(r'\D', '', matches[0])
                    #     phone_number.append(clean_num)
                    # else:
                    #     # Якщо формат інший, просто чистимо все крім цифр
                    #     clean_num = re.sub(r'\D', '', extracted_text)
                    #     if len(clean_num) >= 10:
                    #         phone_number.append(clean_num)



            # btn_selector = 'button.size-large.conversion[data-action="showBottomPopUp"]'
            #
            # try:
            #     btn = page.locator(btn_selector).first
            #     if await btn.is_visible():
            #         await btn.click(force=True)
            #
            #         # SMART WAIT: Чекаємо поки в будь-якому місці з'явиться номер
            #         try:
            #             await page.wait_for_function("""
            #                 () => {
            #                     // 1. Чи з'явився лінк tel:?
            #                     const link = document.querySelector('a[href^="tel:"]');
            #                     if (link) return true;
            #
            #                     // 2. Чи змінився текст ПЕРШОЇ кнопки на цифри?
            #                     const btn = document.querySelector('button[data-action="showBottomPopUp"]');
            #                     if (btn) {
            #                         // Рахуємо цифри саме в цій кнопці
            #                         const text = btn.innerText;
            #                         const digitCount = (text.match(/\d/g) || []).length;
            #                         // (097) 123 45 67 -> 10 цифр. (097) XXX XX XX -> 3 цифри.
            #                         return digitCount >= 10;
            #                     }
            #                     return false;
            #                 }
            #             """, timeout=5000)  # Даємо 5 сек на підвантаження
            #         except:
            #             pass
            # except Exception:
            #     pass


            # --- ПРІОРИТЕТ 2: Перебір тексту кнопок (Виправлення гігантського номера) ---
            # Ми не зливаємо весь текст. Ми беремо кожну кнопку окремо.
            # if not found_phones:
            #     buttons = sel.css(btn_selector)
            #     for btn_node in buttons:
            #         # Отримуємо текст конкретної кнопки
            #         # join тут потрібен, бо всередині button може бути декілька span
            #         btn_text = "".join(btn_node.css('::text').getall())
            #
            #         # Швидка перевірка: чи схоже це на повний номер?
            #         # Шукаємо хоча б 7 цифр підряд або патерн (0XX) XXX
            #         import re
            #         digit_count = len(re.findall(r'\d', btn_text))
            #         if digit_count >= 10:
            #             found_phones.append(btn_text)
            #             # Якщо знайшли хоча б один хороший номер - зупиняємось (щоб не гаяти час)
            #             break

                        # --- ПРІОРИТЕТ 3: Fallback (Popup) ---
            # import re
            # if not found_phones:
            #     # Іноді номер відкривається в модальному вікні, а не в кнопці
            #     popup_text = sel.css('.popup-body ::text, .popup-inner ::text').getall()
            #     for p_text in popup_text:
            #         if len(re.findall(r'\d', p_text)) >= 10:
            #             found_phones.append(p_text)

            # # --- ВАЛІДАЦІЯ ПЕРЕД ЗАПИСОМ ---
            # valid_phones_for_loader = []
            # for p in found_phones:
            #     # Очищаємо від сміття
            #     digits_only = re.sub(r'\D', '', str(p))
            #
            #     # Фінальний фільтр: пропускаємо (097) XXX XX XX (3 цифри)
            #     # Пропускаємо {38097...093...} (якщо раптом щось злиплось, хоча цикл вище це фіксить)
            #     # Беремо тільки адекватну довжину номера (10-12 цифр)
            #     if 10 <= len(digits_only) <= 13:
            #         valid_phones_for_loader.append(p)
            #     elif len(digits_only) > 13:
            #         # Якщо все ж таки склеїлось (малоймовірно), спробуємо взяти перші 12
            #         self.logger.warning(f"⚠️ Phone too long, cutting: {digits_only}")
            #         valid_phones_for_loader.append(digits_only[:12])
            #     else:
            #         self.logger.warning(f"⚠️ Ignored trash/incomplete: {p}")
            found_phones = []

            # --- ПРІОРИТЕТ 1: Посилання tel: (Найточніше) ---
            # Це працює, якщо номер став клікабельним


            content = await page.content()

            sel = Selector(text=content)
            # --- ЗАПОВНЕННЯ ITEM ---
            loader = ItemLoader(item=ScraperAutoriaItem(), selector=sel)

            # Передаємо список (навіть якщо там 1 номер - це ок, loader розбереться)
            loader.add_value('phone_number', found_phones)


            yield loader.load_item()

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {e}")
        finally:
            await page.close()

    async def _extract_phone_number(self, page: Page) -> str:
        phone_number = None
        btn_selector = 'button.size-large.conversion[data-action="showBottomPopUp"]'
        try:
            # Чекаємо кнопку
            await page.wait_for_selector(btn_selector, state='visible', timeout=10000)
            btn = page.locator(btn_selector).first
            await btn.scroll_into_view_if_needed()
            await asyncio.sleep(1)
            # Click with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await btn.click(force=True)
                    self.logger.info(f"✅ Phone button clicked (attempt {attempt + 1})")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(1)  # Wait before retry
        except Exception as e:
            self.logger.warning(f"Click failed: {e}")
        try:
            # У вашому тесті ви берете текст з div.popup-inner ... span
            target_selector = 'div.popup-inner button.size-large.conversion span'
            self.logger.info(f"📞 Found target selector: {target_selector}")
            # Чекаємо поки з'явиться текст (номер)
            await page.wait_for_selector(target_selector, timeout=10000)

            # Отримуємо текст
            extracted_text = await page.inner_text(target_selector)
            self.logger.info(f"📞 Raw text from button: {extracted_text}")
        except Exception as e:
            self.logger.warning(f"Text extraction failed: {e}")
        hrefs = loader.css('a[href^="tel:"]::attr(href)').getall()
        for href in hrefs:
            # tel:+38097... -> +38097...
            found_phones.append(href)
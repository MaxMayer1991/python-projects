from playwright.async_api import Page
from scrapy.loader import ItemLoader
from ..items import ScraperAutoriaItem
import os, scrapy
import asyncio
from scrapy.selector import Selector

class AutoriaSpider(scrapy.Spider):
    name = "autoria"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/car/used/"]

    async def start(self):
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

    async def parse_car_page(self, response) -> None:
        try:
            # Add a timeout for the entire parsing process
            async for item in self._parse_car_page(response):
                yield item
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout while parsing {response.url}")
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")

    async def _parse_car_page(self, response):
        page: Page = response.meta.get('playwright_page')

        if not page:
            return

        try:
            self.logger.info(f"Processing: {response.url}")
            page.set_default_timeout(30000)

            # Initialize loader with response
            loader = ItemLoader(item=ScraperAutoriaItem(), response=response)
            loader.add_value('url', response.url)

            # First, collect all static data
            try:
                # Wait for the page to fully load
                await page.wait_for_selector('div#sellerInfo', state='attached', timeout=15000)

                # Collect all static data
                content = await page.content()
                sel = Selector(text=content)

                # Fill basic fields
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

            # Handle phone number extraction
            phone_number = await self._extract_phone_number(page)
            if phone_number:
                loader.add_value('phone_number', phone_number)
            else:
                self.logger.warning("Could not extract phone number")

            # Yield the item with all collected data
            yield loader.load_item()

        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")
        finally:
            try:
                if not page.is_closed():
                    await page.close()
            except:
                pass

    async def _extract_phone_number(self, page: Page) -> str:
        """Extract phone number from the page with retries and proper waiting."""
        try:
            # Define selectors
            phone_btn_selector = 'button.size-large.conversion[data-action="showBottomPopUp"]'
            phone_text_selector = 'div.popup-inner button.size-large.conversion span'

            # Wait for the phone button to be visible
            try:
                btn = await page.wait_for_selector(
                    phone_btn_selector,
                    state='attached',
                    timeout=5000
                )
                await btn.wait_for_element_state('visible', timeout=3000)
            except Exception as e:
                self.logger.warning(f"Phone button not found: {e}")
                return ""

            # Scroll to the button and click
            btn = page.locator(phone_btn_selector).first
            await btn.scroll_into_view_if_needed()
            await asyncio.sleep(1)  # Small delay for stability
            # Click with retry logic
            for attempt in range(3):
                try:
                    await btn.click(force=True)
                    self.logger.info(f"✅ Phone button clicked (attempt {attempt + 1})")
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        self.logger.warning(f"Failed to click phone button: {e}")
                        return ""
                    await asyncio.sleep(1)

            # Wait for the phone number to appear
            try:
                await page.wait_for_selector(phone_text_selector, state='visible', timeout=10000)
                phone_elem = await page.query_selector(phone_text_selector)

                if phone_elem:
                    phone_text = await phone_elem.inner_text()
                    self.logger.info(f"📞 Found phone: {phone_text}")
                    return phone_text.strip()
            except Exception as e:
                self.logger.warning(f"Phone number not found: {e}")
                return ""

        except Exception as e:
            self.logger.error(f"Error in phone extraction: {e}")

        return ""
        #
        #     except Exception as e:
        #         self.logger.warning(f"Phone number not found: {e}")
        #         return ""
        #
        # except Exception as e:
        #     self.logger.error(f"Error in phone extraction: {e}")
        #
        # return ""
        #     # Scroll into view and click with retries
        #     max_retries = 2
        #     for attempt in range(max_retries):
        #         try:
        #             await btn.scroll_into_view_if_needed()
        #             await asyncio.sleep(0.5)  # Reduced delay
        #
        #             # Use Promise.race to wait for either the phone number or timeout
        #             phone_text = await page.evaluate("""
        #                    async ([btnSelector, phoneSelector]) => {
        #                        // Click the button
        #                        const btn = document.querySelector(btnSelector);
        #                        btn.click();
        #
        #                        // Wait for phone number to appear with a timeout
        #                        return await new Promise((resolve) => {
        #                            // Check immediately in case it's already there
        #                            const phoneEl = document.querySelector(phoneSelector);
        #                            if (phoneEl && phoneEl.innerText.trim()) {
        #                                return resolve(phoneEl.innerText.trim());
        #                            }
        #
        #                            // If not found, set up a mutation observer
        #                            const observer = new MutationObserver((mutations, obs) => {
        #                                const phoneEl = document.querySelector(phoneSelector);
        #                                if (phoneEl && phoneEl.innerText.trim()) {
        #                                    obs.disconnect();
        #                                    resolve(phoneEl.innerText.trim());
        #                                }
        #                            });
        #
        #                            // Start observing the document with the configured parameters
        #                            observer.observe(document.body, {
        #                                childList: true,
        #                                subtree: true
        #                            });
        #
        #                            // Set a timeout to avoid hanging
        #                            setTimeout(() => {
        #                                observer.disconnect();
        #                                resolve(null);
        #                            }, 3000);  // Reduced from 10s to 3s
        #                        });
        #                    }
        #                """, [phone_btn_selector, phone_text_selector])
        #
        #             if phone_text:
        #                 self.logger.info(f"📞 Found phone: {phone_text}")
        #                 return phone_text
        #
        #         except Exception as e:
        #             if attempt == max_retries - 1:
        #                 self.logger.warning(f"Failed to get phone number after {max_retries} attempts: {e}")
        #             await asyncio.sleep(0.5)  # Small delay before retry
        #
        # except Exception as e:
        #     self.logger.error(f"Error in phone extraction: {e}")
        #
        #
        # return ""

        #     # Click with retry logic
        #     for attempt in range(3):
        #         try:
        #             await btn.click(force=True)
        #             self.logger.info(f"✅ Phone button clicked (attempt {attempt + 1})")
        #             break
        #         except Exception as e:
        #             if attempt == 2:  # Last attempt
        #                 self.logger.warning(f"Failed to click phone button: {e}")
        #                 return ""
        #             await asyncio.sleep(1)
        #
        #     # Wait for the phone number to appear
        #     try:
        #         await page.wait_for_selector(phone_text_selector, state='visible', timeout=10000)
        #         phone_elem = await page.query_selector(phone_text_selector)
        #
        #         if phone_elem:
        #             phone_text = await phone_elem.inner_text()
        #             self.logger.info(f"📞 Found phone: {phone_text}")
        #             return phone_text.strip()
        #
        #     except Exception as e:
        #         self.logger.warning(f"Phone number not found: {e}")
        #         return ""
        #
        # except Exception as e:
        #     self.logger.error(f"Error in phone extraction: {e}")
        #
        # return ""
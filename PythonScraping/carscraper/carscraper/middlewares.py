from scrapy import signals
# useful for handling different item types with a single interface

from urllib.parse import urlencode
from random import randint
import requests

class ScrapeOpsFakeUserAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    def __init__(self,settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT','http://headers.scrapeops.io/v1/user-agents?')
        self.scrapeops_fake_user_agents_active = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENABLED', False)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.header_list = []
        self._get_user_agent_list()
        self._scrapeops_fake_user_agents_enabled()
    def _get_user_agent_list(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.user_agents_list = json_response.get('result',[])

    def _get_random_user_agent(self):
        random_index = randint(0, len(self.user_agents_list) - 1)
        return self.user_agents_list[random_index]
    def _scrapeops_fake_user_agents_enabled(self):
        if self.scrapeops_api_key is not None and self.scrapeops_api_key != '' or self.scrapeops_fake_user_agents_active == False:
            self.scrapeops_fake_user_agents_active = False
        else:
            self.scrapeops_fake_user_agents_active = True
    def process_request(self, request, spider):
        random_user_agent = self._get_random_user_agent()
        request.headers['User-Agent'] = random_user_agent
        spider.logger.debug(f"Using User-Agent: {random_user_agent}")
        print("***************** NEW USER-AGENT ATTACHED *********************")
        print(request.headers['User-Agent'])

class ScrapeOpsFakeBrowserHeaderAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT', 'https://headers.scrapeops.io/v1/browser-headers')
        self.scrapeops_fake_browser_headers_active = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED', True)
        self.scrapeops_num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []
        self._get_headers_list()
        self._scrapeops_fake_browser_headers_enabled()

    def _get_headers_list(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.scrapeops_num_results is not None:
            payload['num_results'] = self.scrapeops_num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        json_response = response.json()
        self.headers_list = json_response.get('result', [])

    def _get_random_browser_header(self):
        random_index = randint(0, len(self.headers_list) - 1)
        return self.headers_list[random_index]

    def _scrapeops_fake_browser_headers_enabled(self):
        if self.scrapeops_api_key is None or self.scrapeops_api_key == '' or self.scrapeops_fake_browser_headers_active == False:
            self.scrapeops_fake_browser_headers_active = False
        else:
            self.scrapeops_fake_browser_headers_active = True

    def process_request(self, request, spider):
        random_browser_header = self._get_random_browser_header()

        request.headers['accept-language'] = random_browser_header.get('accept-language')
        request.headers['sec-fetch-user'] = random_browser_header.get('sec-fetch-user')
        request.headers['sec-fetch-mod'] = random_browser_header.get('sec-fetch-mod')
        request.headers['sec-fetch-site'] = random_browser_header.get('sec-fetch-site')
        request.headers['sec-ch-ua-platform'] = random_browser_header.get('sec-ch-ua-platform')
        request.headers['sec-ch-ua-mobile'] = random_browser_header.get('sec-ch-ua-mobile')
        request.headers['sec-ch-ua'] = random_browser_header.get('sec-ch-ua')
        request.headers['accept'] = random_browser_header.get('accept')
        request.headers['user-agent'] = random_browser_header.get('user-agent')
        request.headers['upgrade-insecure-requests'] = random_browser_header.get('upgrade-insecure-requests')

        print("***************** NEW HEADER ATTACHED *********************")
        print(request.headers)
class ProxyMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        url  = crawler.settings.get('PROXY_URL')
        return cls(url)
    def __init__(self, proxy_url):
        self.proxy_url  = proxy_url

    def process_request(self, request, spider):
        if self.proxy_url:
            request.meta['proxy'] = self.proxy_url


class PlaywrightContextMiddleware:
    """
    Цей middleware бере User-Agent, який згенерував ScrapeOps (або інший middleware),
    і передає його в налаштування браузера Playwright.
    """

    def process_request(self, request, spider):
        # Працюємо тільки якщо це Playwright-запит
        if not request.meta.get('playwright'):
            return

        # 1. Синхронізація User-Agent
        # ScrapeOps встановлює UA в headers. Ми беремо його звідти.
        ua = request.headers.get('User-Agent')
        if ua:
            # Декодуємо bytes в str
            ua_str = ua.decode('utf-8')

            # Ініціалізуємо словник kwargs, якщо його немає
            request.meta.setdefault('playwright_context_kwargs', {})

            # Встановлюємо UA на рівні браузера (це змінює navigator.userAgent в JS)
            request.meta['playwright_context_kwargs']['user_agent'] = ua_str

            spider.logger.debug(f"🕷️ Playwright Context UA set to: {ua_str}")

        # 2. Проксі обробляється автоматично через request.meta['proxy'],
        # який встановлює ваш існуючий ProxyMiddleware.
        # Додаткових дій тут не потрібно.

        return None
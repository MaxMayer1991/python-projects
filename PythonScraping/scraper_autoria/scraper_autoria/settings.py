import os
from dotenv import load_dotenv
from scrapy.utils.request import RequestFingerprinter
import sys
import asyncio
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

# REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.6"
BOT_NAME = "scraper_autoria"

DATABASE_URL = os.getenv('DATABASE_URL')

SPIDER_MODULES = ["scraper_autoria.spiders"]
NEWSPIDER_MODULE = "scraper_autoria.spiders"

PLAYWRIGHT_BROWSER_TYPE = "firefox"

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,          # 🛑 Браузер буде відкриватись у вікні
    # "slow_mo": 1000,            # 🐢 Затримка 1с між діями (щоб ви бачили кліки)
    "timeout": 30 * 1000,       # Таймаут запуску
    "args": [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-component-extensions-with-background-pages",
    ],
# 👇 ЦЕ ВАЖЛИВО ДЛЯ FIREFOX: Вимикаємо прапорець "Я робот"
    "firefox_user_prefs": {
        "dom.webdriver.enabled": False,
        "useAutomationExtension": False,
        "browser.cache.disk.enable": False,  # Не кешувати на диск (швидше)
        "browser.cache.memory.enable": False,
        "permissions.default.image": 2,  # Блокування картинок на рівні рушія Firefox
        "permissions.default.stylesheet": 2,
    }
}
PLAYWRIGHT_CONTEXT_ARGS = {
    "viewport":{"width":1920, "height":1080},
    "device_scale_factor":1,
    "is_mobile": False,          # 👈 Важливо!
    "has_touch": False,          # 👈 Важливо! AutoRIA дивиться на це
    "java_script_enabled": True,
    "locale": "uk-UA",
    "timezone_id": "Europe/Kiev",
    "bypass_csp": True,
    "ignore_https_errors": True,
    "permissions": ["notifications"],
    # "service_workers": "allow", # Блокуємо сервіс воркери (часто використовуються для фінгерпринтингу)
}

ADDONS = {}

# SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
PROXY_URL = os.getenv('PROXY_URL')
# SCRAPEOPS_PROXY_ENABLED = True
# SCRAPEOPS_PROXY_SETTINGS = {'country': 'ua'}
# SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = 'https://headers.scrapeops.io/v1/user-agents'
# SCRAPEOPS_FAKE_USER_AGENT_ENABLED = True
# SCRAPEOPS_NUM_RESULTS = 5
PLAYWRIGHT_MAX_CONTEXTS = 4
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 403]

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

DOWNLOADER_MIDDLEWARES = {
    # Вимикаємо стандартний UserAgent middleware, щоб не заважав
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 1. Спочатку ставимо проксі (ваш існуючий)
    'scraper_autoria.middlewares.ProxyMiddleware': 350,
    # 2. Потім ScrapeOps генерує заголовки та UA
    # 'scraper_autoria.middlewares.ScrapeOpsFakeUserAgentMiddleware': 370,
    # 'scraper_autoria.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 380,
    # 3. ВАЖЛИВО: Наш новий middleware має йти ПІСЛЯ ScrapeOps, але ДО хендлера
    'scraper_autoria.middlewares.PlaywrightContextMiddleware': 400
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "scraper_autoria.pipelines.PostgreSQLPipeline": 300
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 3600
# HTTPCACHE_DIR = "httpcache"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

PLAYWRIGHT_ABORT_REQUEST = lambda req: (
    req.resource_type in {"image", "media", "other"}
)
# Рівень логування для Scrapy
LOG_LEVEL = 'INFO'

# Вимикаємо/фільтруємо шумні логи бібліотек
import logging
logging.getLogger('scrapy_playwright').setLevel(logging.WARNING)
logging.getLogger('playwright').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 4
#CONCURRENT_REQUESTS_PER_IP = 16
# Збільшуємо таймаут Playwright
# PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000
# Disable cookies (enabled by default)
#COOKIES_ENABLED = False
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "scraper_autoria.middlewares.ScraperAutoriaSpiderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"


# settings.py

# def remove_unsafe_headers(browser_type_name, playwright_request, scrapy_request_data):
#     """
#     1. Removes the Proxy-Authorization header to prevent Playwright 'Unsafe header' errors.
#     2. Converts all other headers from bytes (Scrapy) to strings (Playwright).
#     """
#     headers = scrapy_request_data.get('headers')
#     if not headers:
#         return None
#
#     new_headers = {}
#
#     for name, value in headers.items():
#         # 1. Decode header NAME (key)
#         if isinstance(name, bytes):
#             name_str = name.decode('utf-8')
#         else:
#             name_str = str(name)
#
#         # 2. FILTER: Skip the forbidden header
#         if name_str.lower() == 'proxy-authorization':
#             continue
#
#         # 3. Decode header VALUE
#         if isinstance(value, list):
#             # Join list of bytes into a single string: [b'v1', b'v2'] -> "v1, v2"
#             value_str = b", ".join(value).decode('utf-8')
#         elif isinstance(value, bytes):
#             value_str = value.decode('utf-8')
#         else:
#             value_str = str(value)
#
#         new_headers[name_str] = value_str
#
#     return new_headers
# Register the function
# PLAYWRIGHT_PROCESS_REQUEST_HEADERS = remove_unsafe_headers

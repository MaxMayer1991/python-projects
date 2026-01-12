import os
from dotenv import load_dotenv
load_dotenv()

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# PLAYWRIGHT_BROWSER_TYPE = "chromium"
BOT_NAME = "carscraper"
SPIDER_MODULES = ["carscraper.spiders"]
NEWSPIDER_MODULE = "carscraper.spiders"
# SCRAPEOPS_API_KEY = os.getenv('SCRAPEOPS_API_KEY')
PROXY_URL = os.getenv('PROXY_URL')
# SCRAPEOPS_PROXY_ENABLED = True
# SCRAPEOPS_PROXY_SETTINGS = {'country': 'ua'}
# SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT = 'https://headers.scrapeops.io/v1/user-agents'
# SCRAPEOPS_FAKE_USER_AGENT_ENABLED = True
# SCRAPEOPS_NUM_RESULTS = 5
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
# Increased concurrency for better performance
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_ITEMS = 100

# Playwright settings
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # Changed to True for production
    "timeout": 30 * 1000,  # 30 seconds
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox"
    ]
}
PLAYWRIGHT_CONTEXT_ARGS = {
    "ignore_https_errors": True
}
PLAYWRIGHT_ABORT_REQUEST = lambda req: (
    req.resource_type == "image"
    or req.resource_type == "media"
    or req.resource_type == "font"
    or ".googletagmanager.com" in req.url
    or "doubleclick.net" in req.url
)
PLAYWRIGHT_VIEWPORT = {
    "default": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    }
}
# Better retry settings
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Disable cookies unless needed
COOKIES_ENABLED = False

# Disable Telnet console (enabled by default)
TELNETCONSOLE_ENABLED = False
# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2
# The download delay setting will honor only one of:
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True
# Only use Playwright for specific requests by default
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Middleware settings

DOWNLOADER_MIDDLEWARES = {
    # Вимикаємо стандартний middleware, щоб він не ліз із заголовком Proxy-Authorization
    #'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
    # Вимикаємо стандартний UserAgent middleware, щоб не заважав
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 1. Спочатку ставимо проксі (ваш існуючий)
    'carscraper.middlewares.ProxyMiddleware': 350,

    # 2. Потім ScrapeOps генерує заголовки та UA
    'carscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 370,
    'carscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 380,

    # 3. ВАЖЛИВО: Наш новий middleware має йти ПІСЛЯ ScrapeOps, але ДО хендлера
    'carscraper.middlewares.PlaywrightContextMiddleware': 400


}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "carscraper.pipelines.PostgreSQLPipeline": 300
}
DATABASE_URL = os.getenv('DATABASE_URL')
# Set settings whose default value is deprecated to a future-proof value

# FEED_EXPORT_ENCODING = "utf-8"
def remove_unsafe_headers(browser_type_name, playwright_request, scrapy_request_data):
    """
    1. Видаляє заголовок Proxy-Authorization (щоб не сварився Playwright).
    2. Конвертує заголовки з bytes (Scrapy style) у strings (Playwright style).
    """
    headers = scrapy_request_data.get('headers')
    if not headers:
        return None

    new_headers = {}

    for name, value in headers.items():
        # 1. Декодуємо КЛЮЧ (назву заголовка)
        # Scrapy: b'User-Agent' -> Playwright: 'User-Agent'
        if isinstance(name, bytes):
            name_str = name.decode('utf-8')
        else:
            name_str = str(name)

        # 2. Фільтруємо небезпечний заголовок
        if name_str.lower() == 'proxy-authorization':
            continue

        # 3. Декодуємо ЗНАЧЕННЯ
        # Scrapy зберігає значення як список байтів: [b'value'] або просто b'value'
        if isinstance(value, list):
            # Об'єднуємо список і декодуємо: [b'v1', b'v2'] -> "v1, v2"
            value_str = b", ".join(value).decode('utf-8')
        elif isinstance(value, bytes):
            value_str = value.decode('utf-8')
        else:
            value_str = str(value)

        new_headers[name_str] = value_str

    return new_headers

# 3. Активуємо цю функцію
PLAYWRIGHT_PROCESS_REQUEST_HEADERS = remove_unsafe_headers
import os
import logging
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline():
    # Load environment variables
    load_dotenv()
    
    # Get settings
    settings = get_project_settings()
    
    # Enable only the PostgreSQL pipeline
    settings.set('ITEM_PIPELINES', {
        'carscraper.pipelines.PostgreSQLPipeline': 300,
    })
    
    # Disable other components that might interfere
    settings.set('DOWNLOADER_MIDDLEWARES', {})
    settings.set('SPIDER_MIDDLEWARES', {})
    settings.set('EXTENSIONS', {})
    
    # Log the database URL (without password)
    db_url = settings.get('DATABASE_URL') or os.getenv('DATABASE_URL')
    if db_url:
        # Mask password in the log
        import re
        safe_url = re.sub(r':[^@]+@', ':***@', db_url)
        logger.info(f"Using database URL: {safe_url}")
    
    # Create a test item
    test_item = {
        'url': 'https://example.com/test-item',
        'title': 'Test Item',
        'price_usd': 10000,
        'odometer': 50000,
        'username': 'test_user',
        'phone_number': ['+1234567890'],
        'image_url': ['https://example.com/image.jpg'],
        'image_count': 1,
        'car_number': 'AA1234BB',
        'car_vin': 'WBA12345678901234',
    }
    
    # Create a test spider that yields the test item
    from scrapy import Spider
    
    class TestSpider(Spider):
        name = 'test_spider'
        
        def start_requests(self):
            yield scrapy.Request('https://example.com', self.parse)
            
        def parse(self, response):
            yield test_item
    
    # Run the test
    try:
        process = CrawlerProcess(settings)
        process.crawl(TestSpider)
        logger.info("Starting test spider...")
        process.start()
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    test_pipeline()

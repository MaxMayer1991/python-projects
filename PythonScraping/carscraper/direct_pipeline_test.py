import os
import logging
from dotenv import load_dotenv
from carscraper.pipelines import PostgreSQLPipeline

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_pipeline():
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL is not set in environment variables")
    
    logger.info("Starting pipeline test...")
    
    # Create pipeline instance
    try:
        logger.info("Creating PostgreSQLPipeline instance...")
        pipeline = PostgreSQLPipeline(db_url)
        logger.info("Pipeline created successfully")
        
        # Create a test item
        test_item = {
            'url': 'https://example.com/test-item-direct',
            'title': 'Direct Test Item',
            'price_usd': 15000,
            'odometer': 25000,
            'username': 'test_user_direct',
            'phone_number': ['+1234567890'],
            'image_url': ['https://example.com/image_direct.jpg'],
            'image_count': 1,
            'car_number': 'AA9999BB',
            'car_vin': 'WBA99999999999999',
        }
        
        # Process the item
        logger.info("Processing test item...")
        processed_item = pipeline.process_item(test_item, None)  # None for spider
        logger.info(f"Item processed successfully: {processed_item}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False
    finally:
        # Clean up
        if 'pipeline' in locals():
            try:
                pipeline.close_spider(None)
                logger.info("Pipeline closed")
            except Exception as e:
                logger.error(f"Error closing pipeline: {e}")

if __name__ == "__main__":
    if test_pipeline():
        logger.info("✅ Pipeline test completed successfully!")
    else:
        logger.error("❌ Pipeline test failed")

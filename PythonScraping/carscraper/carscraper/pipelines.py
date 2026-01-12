# pipelines.py
import logging
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
from psycopg2 import pool
from datetime import datetime
import os
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)


class PostgreSQLPipeline:
    """
    Stores items in the cars table with connection pooling.
    """
    TABLE_NAME = "car_products"

    def __init__(self, database_url: str):
        logger.info("4.1. Initializing PostgreSQLPipeline with database URL")
        self.database_url = database_url
        self.connection_pool = None
        self.retry_attempts = 3
        self.retry_delay = 2  # seconds
        logger.info("4.2. Starting connection pool initialization...")
        self._initialize_pool()
        logger.info("4.3. Connection pool initialization completed")

    def _initialize_pool(self):
        """Initialize the connection pool"""
        logger.info("4.2.1. Starting to parse database URL")
        try:
            # Parse the connection string
            import urllib.parse as urlparse
            result = urlparse.urlparse(self.database_url)
            username = result.username
            password = '***' if result.password else 'None'  # Don't log actual password
            database = result.path[1:]  # Remove leading '/'
            hostname = result.hostname
            port = result.port or 5432

            logger.info(
                f"4.2.2. Parsed connection details - Host: {hostname}, Port: {port}, DB: {database}, User: {username}")

            # Extract query parameters
            query = dict(urlparse.parse_qsl(result.query))
            logger.debug(f"4.2.3. Query parameters: {query}")

            # Add connect_timeout to query parameters if not already present
            if 'connect_timeout' not in query:
                query['connect_timeout'] = '5'  # 5 seconds timeout

            logger.info(
                f"4.2.4. Connection parameters: host={hostname}, port={port}, dbname={database}, user={username}, connect_timeout={query['connect_timeout']}")

            # Create connection pool with timeout
            logger.info("4.2.5. Creating connection pool...")

            try:
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=hostname,
                    port=port,
                    user=username,
                    password=result.password,  # Use actual password here
                    dbname=database,
                    **query
                )
                logger.info("4.2.6. Successfully created database connection pool")

                # Test the connection
                self._test_connection()

            except psycopg2.Error as e:
                logger.error(f"4.2.7. Failed to create connection pool: {str(e)}")
                self.connection_pool = None
                raise

        except Exception as e:
            logger.error(f"4.2.8. Failed to initialize connection pool: {e}")
            self.connection_pool = None
            raise

    def _test_connection(self):
        """Test the database connection"""
        logger.info("4.2.7. Testing database connection...")
        conn = None
        try:
            logger.info("4.2.8. Getting connection from pool...")
            conn = self.connection_pool.getconn()
            logger.info("4.2.9. Got connection, creating cursor...")

            with conn.cursor() as cur:
                logger.info("4.2.10. Executing test query...")
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    logger.info("4.2.11. Successfully connected to the database")
                else:
                    logger.error("4.2.11. Unexpected result from database connection test")
                    raise Exception("Unexpected test query result")

        except psycopg2.Error as e:
            logger.error(f"4.2.12. Database connection test failed: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"4.2.12. Unexpected error in database connection test: {e}", exc_info=True)
            raise
        finally:
            if conn:
                logger.info("4.2.13. Returning connection to pool")
                self.connection_pool.putconn(conn)

    @classmethod
    def from_crawler(cls, crawler):
        logger.info("1. Starting PostgreSQLPipeline initialization...")

        try:
            # Get database URL
            logger.info("2. Getting DATABASE_URL from settings or environment...")
            db_url = crawler.settings.get("DATABASE_URL") or os.getenv("DATABASE_URL")
            if not db_url:
                error_msg = "DATABASE_URL is not set in settings or environment variables"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("3. Database URL found")
            logger.debug(f"Database URL: {db_url}")

            # Create pipeline instance
            logger.info("4. Creating PostgreSQLPipeline instance...")
            pipeline = cls(db_url)

            logger.info("5. PostgreSQLPipeline instance created successfully")
            return pipeline

        except Exception as e:
            logger.error(f"ERROR in from_crawler: {str(e)}", exc_info=True)
            raise

    def open_spider(self, spider):
        """Called when the spider is opened"""
        spider_name = getattr(spider, 'name', 'unknown')
        logger.info(f"Spider opened: {spider_name}")
        if not self.connection_pool:
            logger.error("Connection pool not initialized")
            raise RuntimeError("Database connection pool not initialized")

    def close_spider(self, spider):
        """Called when the spider is closed"""
        spider_name = getattr(spider, 'name', 'unknown')
        logger.info(f"Closing spider and cleaning up: {spider_name}")
        
        try:
            if hasattr(self, 'connection_pool') and self.connection_pool:
                logger.info("Closing database connection pool...")
                self.connection_pool.closeall()
                logger.info("Successfully closed all database connections")
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
        finally:
            # Ensure we don't try to use the pool after closing
            if hasattr(self, 'connection_pool'):
                del self.connection_pool

    def process_item(self, item, spider):
        """Process each item with retry logic"""
        ad = ItemAdapter(item)
        url = ad.get("url")

        # Get logger from spider or use module logger if spider is None
        logger = getattr(spider, 'logger', logging.getLogger(__name__))

        if not url:
            raise DropItem("Missing URL in item")

        last_exception = None

        # Retry logic for database operations
        for attempt in range(self.retry_attempts):
            conn = None
            try:
                # Get a connection from the pool
                conn = self.connection_pool.getconn()
                with conn.cursor() as cur:
                    # Check if item exists
                    cur.execute(f"SELECT id FROM {self.TABLE_NAME} WHERE url = %s", (url,))
                    row = cur.fetchone()

                    if row:
                        self._update_item(cur, ad, row[0])
                        logger.info(f"Updated existing item: {url}")
                    else:
                        self._insert_item(cur, ad)
                        logger.info(f"Inserted new item: {url}")

                    conn.commit()
                    return item

            except Exception as e:
                if conn:
                    conn.rollback()
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_attempts} failed for {url}: {e}"
                )
                if attempt < self.retry_attempts - 1:
                    import time
                    time.sleep(self.retry_delay * (attempt + 1))
            finally:
                if conn:
                    self.connection_pool.putconn(conn)

        # If we get here, all retries failed
        error_msg = f"Failed to process item after {self.retry_attempts} attempts: {url}"
        if last_exception:
            error_msg += f": {str(last_exception)}"
        logger.error(error_msg, exc_info=True)
        raise DropItem(error_msg)

    def _insert_item(self, cursor, ad):
        """Insert a new item into the database"""
        try:
            cols = [
                "url", "title", "price_usd", "odometer", "username",
                "phone_number", "image_url", "image_count", "car_number",
                "car_vin", "datetime_found"
            ]

            # Ensure phone numbers are in the correct format (array of text)
            phone_numbers = ad.get("phone_number", [])
            if not isinstance(phone_numbers, (list, tuple)):
                phone_numbers = [phone_numbers] if phone_numbers else []
            phone_numbers = [str(pn) for pn in phone_numbers if pn]

            values = [
                ad.get("url"),
                ad.get("title"),
                ad.get("price_usd"),
                ad.get("odometer"),
                ad.get("username"),
                phone_numbers,
                ad.get("image_url"),
                ad.get("image_count"),
                ad.get("car_number"),
                ad.get("car_vin"),
                datetime.utcnow(),
            ]

            placeholders = ", ".join(["%s"] * len(cols))
            query = f"""
                INSERT INTO {self.TABLE_NAME} ({', '.join(cols)})
                VALUES ({placeholders})
                RETURNING id
            """

            cursor.execute(query, values)
            return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error in _insert_item: {e}", exc_info=True)
            raise

    def _update_item(self, cursor, ad, item_id):
        """Update an existing item in the database"""
        try:
            updates = []
            values = []

            # Add all fields that should be updated
            for field in ["title", "price_usd", "odometer", "username",
                          "phone_number", "image_url", "image_count",
                          "car_number", "car_vin"]:
                if field in ad:
                    if field == "phone_number":
                        # Handle phone numbers array
                        phone_numbers = ad.get("phone_number", [])
                        if not isinstance(phone_numbers, (list, tuple)):
                            phone_numbers = [phone_numbers] if phone_numbers else []
                        phone_numbers = [str(pn) for pn in phone_numbers if pn]
                        updates.append(f"{field} = %s")
                        values.append(phone_numbers)
                    else:
                        updates.append(f"{field} = %s")
                        values.append(ad[field])

            # Add the updated timestamp
            updates.append("datetime_updated = %s")
            values.append(datetime.utcnow())

            # Add the item_id for the WHERE clause
            values.append(item_id)

            query = f"""
                UPDATE {self.TABLE_NAME}
                SET {', '.join(updates)}
                WHERE id = %s
            """

            cursor.execute(query, values)

        except Exception as e:
            logger.error(f"Error in _update_item: {e}", exc_info=True)
            raise
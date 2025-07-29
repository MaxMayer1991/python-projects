# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2

class BookscraperPipeline:
    def process_item(self, item, spider):
        return item

class SavingToPostgresPipeline(object):
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        try:
            self.connection = psycopg2.connect(
                host='localhost',
                user='postgres',
                password='eduroam', #your password
                database='books_data',
                port='5432'
            )
            self.cur = self.connection.cursor()
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    def create_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS book_products (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    price NUMERIC,
                    url TEXT UNIQUE
                )
            """)
            self.connection.commit()
        except Exception as e:
            print(f"Error creating table: {e}")
            raise

    def process_item(self, item, spider):
        try:
            self.cur.execute("""
                INSERT INTO book_products (title, price, url) 
                VALUES (%s, %s, %s)
                ON CONFLICT (url) DO NOTHING
        """,(item['title'],item['price'],item['url']))
            self.connection.commit()
        except Exception as e:
            print(f"Error inserting data: {e}")
            self.connection.rollback()
            raise
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
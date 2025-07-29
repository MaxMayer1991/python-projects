# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2
class PostgresDemoPipeLine:
    def __init__(self):
        ## Connection Details
        hostname='localhost'
        username='postgres'
        password='******' #your password
        database='quotes'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        ## Create quotes table if none exists
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes(
            id serial PRIMARY KEY, 
            url text, 
            title text,
            price_usd INT,
            otometer INT,
            username text,
            phone_number INT,
            image_url text,
            image_count INT,
            car_number text,
            car_vin text,
            datetime_found datetime
        )
        """)
def process_item(self, item, spider):
    self.cur.execute("""INSERT INTO quotes VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
        item['url'],
        item['title'],
        item['price_usd'],
        item['otometer'],
        item['username'],
        item['phone_number'],
        item['image_url'],
        item['image_count'],
        item['car_number'],
        item['car_vin'],
        str(item['datetime_found'])
    ))
    self.connection.commit()
    return item
def close_spider(self, spider):
    ## Close cursor & connection to database
    self.cur.close()
    self.connection.close()

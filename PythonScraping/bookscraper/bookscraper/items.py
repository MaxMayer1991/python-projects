# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from itemloaders.processors import TakeFirst, MapCompose
# from . import loaders as l

def remove_currency(value):
    return float(value.replace('£', ''))

class BookItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(remove_currency), output_processor=TakeFirst())

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import TakeFirst, MapCompose, Compose
from . import loaders as l
import scrapy

class CarItem(scrapy.Item):
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    price_usd = scrapy.Field(
        input_processor=Compose(
            MapCompose(str.strip),    # прибираємо пробіли
            lambda vals: vals,        # збираємо всі у список
            l.choose_price,             # вибираємо рядок з $ або з грн
            l.clean_price               # конвертуємо в int
        ),
        output_processor=TakeFirst()  # беремо єдине число
    )

    odometer = scrapy.Field(
        input_processor=MapCompose(l.clean_odometer),
        output_processor=TakeFirst()
    )
    username = scrapy.Field(
        input_processor=MapCompose(l.clean_value),
        output_processor=TakeFirst()
    )
    phone_number = scrapy.Field(
        input_processor=MapCompose(l.clean_phone_list)
    )
    image_url = scrapy.Field() # Залишаємо як список
    image_count = scrapy.Field(
        input_processor=MapCompose(l.clean_image_count),
        output_processor=TakeFirst()
    )
    car_number = scrapy.Field(
        input_processor=MapCompose(l.clean_value)
    )
    car_vin = scrapy.Field(
        input_processor=MapCompose(l.clean_value)
    )
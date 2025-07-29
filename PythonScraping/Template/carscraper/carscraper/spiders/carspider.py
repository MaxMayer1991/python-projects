import scrapy
from scrapy import Item
from datetime import datetime

# from carscraper.items import CarItem
class CarSpider(scrapy.Spider):
    name = "carspider"
    custom_settings = {'FEED_FORMAT': {'data.csv':{'format':'csv'}}}
    def start_requests(self):
        url = ''
        yield scrapy.Request(url=url, callback=self.parse)
    start_urls = ['https://auto.ria.com/car/used/']
    def parse(self, response):
        # fetch('https://auto.ria.com/car/used/')
        cars = response.css('section.ticket-item')
        for car in cars:
            yield{
                'title' : car.css('a.address span.blue.bold::text').get().strip(),
                'price' : car.css(".price-ticket::attr(data-main-price)").get(),
                'otodometr' : int(car.css("li.item-char.js-race::text").get().strip(' тыс. км '))*1000,
                'car_vin' : car.css('div.base_information span.label-vin span::text').get().strip(),
                'datetime_found' : datetime.now(),
                'link' : car.css(".address::attr(href)").get()
            }


        # # car.css('div.content-bar a::attr(href)').get()
        # car_item = CarItem()
        # car_item['url'] = response.url
        # #car_item['title'] = car.css('a.address span.blue.bold::text').get()
        # #car_item['price_usd'] = car.css(".price-ticket::attr(data-main-price)").get()
        # #car_item['odometer'] = car.css("li.item-char.js-race::text").get()
        # #car_item['car_vin'] = car.css('div.base_information span.label-vin span::text').get()
        # car_item['username'] = products.css("p.product_author a::text").get()
        # car_item['phone_number'] = products.css("p.product_phone::text").get()
        # #car_item['image_url'] = car.css("div.product_img img::attr(src)").attrib
        # car_item['image_url'] = car.xpath('/html/body/div[7]/div[10]/div[4]/main/div[1]/div[1]/div[1]/div[1]/picture/source/@srcset').get()
        # car_item['image_count'] = int(car.xpath('//*[@id="photosBlock"]/div[1]/div[2]/span/span[2]/text()').get().strip('из '))
        # car_item['car_number'] = car.xpath("//*[@id="searchResults"]/section[1]/div[4]/div[2]/div[4]/div/span[1]").get()
        # car_item['datetime_found'] = car.css("p.product_date::text").get()
import scrapy


class UsedcarspiderSpider(scrapy.Spider):
    name = "usedcarspider"
    allowed_domains = ["auto.ria.com/car/used/"]
    start_urls = ["https://auto.ria.com/car/used/"]

    def parse(self, response):
        pass

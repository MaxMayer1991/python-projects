import scrapy
from itemloaders import ItemLoader
from scrapy.loader import ItemLoader
from ..items import BookItem

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        books = response.css(".product_pod")
        for book in books:
            relative_url = book.css("h3 a ::attr(href)").get()

            if "catalogue/" in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = "https://books.toscrape.com/catalogue/" + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if "catalogue/" in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page
            yield response.follow(next_page_url, callback=self.parse)


    def parse_book_page(self, response):
        loader = ItemLoader(item=BookItem(), response=response)
        loader.add_value('url', response.url)
        loader.add_css('title', 'h3 a::text')
        loader.add_css('price', 'div.product_price .price_color::text')
        yield loader.load_item()
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from leroy_merlin.items import LeroyMerlinItem


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/catalogue/{kwargs.get("catalog")}/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="product-image"]')
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyMerlinItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//picture[@slot="pictures"]//source[contains(@media, "1024px")]/@srcset')
        loader.add_xpath('price', '//span[@slot="price"]//text()')
        loader.add_value('url', response.url)
        term = loader.get_xpath("//dt[@class='def-list__term']//text()")
        definition = loader.get_xpath("//dd[@class='def-list__definition']/text ()")
        loader.add_value('params', dict(zip(term, definition)))
        yield loader.load_item()

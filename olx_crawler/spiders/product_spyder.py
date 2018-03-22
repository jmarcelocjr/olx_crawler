import scrapy
import re

class ProductSpyder(scrapy.Spider):
    name = "product"

    start_urls = []

    allowed_domains = ['olx.com.br']

    def __init__(self, url=None):
        self.start_urls.append(url)

    def parse(self, response):
        self.log("Busca: %s" % response.css('title::text').extract_first())

        ul_lista = response.css('ul#main-ad-list')

        for item in ul_lista.css('li.item'):
            url = item.css("a.OLXad-list-link::attr(href)").extract_first()

            if url == None:
                continue

            product = {
                "title": self.removeNewLinesAndTabs(item.css('h3.OLXad-list-title::text').extract_first()),
                "region": self.removeNewLinesAndTabs(item.css('p.detail-region::text').extract_first()),
                "link": item.css('a.OLXad-list-link::attr(href)').extract_first(),
                "price": item.css('p.OLXad-list-price::text').extract_first()
            }

            request = scrapy.Request(url, callback=self.parse_details)

            request.meta['product'] = product
            yield request

    def parse_details(self, response):
        product = response.meta['product']

        product['images'] = list()

        photos = response.css('div.photos')
        for item in photos.css('ul.list > li.item'):
            product['images'].append(item.css('a.link::attr(href)').extract_first())

        product['description'] = self.removeNewLinesAndTabs(response.css('div.OLXad-description p.text::text').extract_first())
        product['seller'] = {
            "name": self.removeNewLinesAndTabs(response.css('div.section_OLXad-user-info li.owner p.text::text').extract_first()),
            "phone": "http:%s" % response.css('div.section_OLXad-user-info li.phone img.number::attr(src)').extract_first(),
        }

        yield product

    def removeNewLinesAndTabs(self, string):
        return string.strip(' ').replace('\n', '').replace('\t', '')

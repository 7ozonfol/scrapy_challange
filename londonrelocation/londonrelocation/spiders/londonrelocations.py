import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from ..property import Property


class LondonrelocationsSpider(scrapy.Spider):
    name = 'londonrelocations'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']
    page_number = 2

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            LondonrelocationsSpider.page_number=2
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):

        all_properties = response.css('.test-box')

        for prop in all_properties:
            property = ItemLoader(item=Property())
            name = prop.css('.h4-space a::text').extract()
            price = prop.css('h5::text').extract()
            url = prop.css('.h4-space a::attr(href)').extract_first()

            i= str(price).index('p')
            clean_price = str(price)[4:i]
            full_url = LondonrelocationsSpider.allowed_domains[0] + str(url)

            property.add_value('title', name)
            property.add_value('price', clean_price)
            property.add_value('url', full_url)

            yield property.load_item()

        next_page = str(response.request.url) + '&pageset='+str(LondonrelocationsSpider.page_number)

        if LondonrelocationsSpider.page_number < 3:
            LondonrelocationsSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse_area_pages)


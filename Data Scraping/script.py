import scrapy
from scrapy.crawler import CrawlerProcess

class FasoNet(scrapy.Spider):
    name='faso.net-scraper'

    def start_requests(self):
        #rubriques urls (société, politique, économie, etc.)
        urls =['https://lefaso.net/spip.php?rubrique4', 'https://lefaso.net/spip.php?rubrique2', 'https://lefaso.net/spip.php?rubrique3', 'https://lefaso.net/spip.php?rubrique62']
        for url in urls:
            yield scrapy.Request(url = url, callback = self.parse_post_url)

    def parse_post_url(self, response):
        #posts blocks
        post_blocks = response.xpath('//content/div[0]//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')
        #posts urls
        post_urls = post_blocks.xpath('.//@href').extract()
        for url in post_urls:
            yield scrapy.Request(url=url, callback=self.parse_infos)
    
    def parse_infos(self, response):
        #retrieve post title and content
        post_title = response.xpath('//h1[@class = "entry-title"]/text()').extract()
        post_content = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')
        post_content = post_content.xpath('//p/text()').extract()
        #Publication date
        publication_date = response.xpath('//content/div[0]/div[0]/div[0]/div[1]/p/text()').extract()
        #retrieve comments
        '''comments section'''
        

process = CrawlerProcess()
process.crawl(FasoNet)
process.start
import scrapy
from scrapy.crawler import CrawlerProcess

class FasoNet(scrapy.Spider):
    name = 'myspider'
    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
    }

    def start_requests(self):
        # rubrics urls (society, politic, economy, etc.)
        rubrics = [
            'https://lefaso.net/spip.php?rubrique4', 
            'https://lefaso.net/spip.php?rubrique2', 
            'https://lefaso.net/spip.php?rubrique3', 
            'https://lefaso.net/spip.php?rubrique62',
            'https://lefaso.net/spip.php?rubrique62',
            'https://lefaso.net/spip.php?rubrique18',
            'https://lefaso.net/spip.php?rubrique5',
            'https://lefaso.net/spip.php?rubrique7'
        ]
        # For each rubric, run through 10 pages
        for base_url in rubrics:
            # Extract rubric ID from rubric url
            rubrique_id = base_url.split('rubrique')[1]
            
            # Parcourir les 10 premières pages
            for page in range(1, 11):
                # First page is the default and correspond the rubric url
                if page == 1:
                    url = base_url
                else:
                    # For other pages, the url structure is different
                    offset = (page - 1) * 20
                    url = f"{base_url}&debut_articles={offset}#pagination_articles"
                
                self.logger.info(f"Planification for a request on rubric {rubrique_id}, page {page}: {url}")
                yield scrapy.Request(
                    url=url, 
                    callback=self.parse_post_url,
                    meta={'rubrique_id': rubrique_id, 'page_num': page}
                )

    def parse_post_url(self, response):
        #Just for log
        rubrique_id = response.meta.get('rubrique_id')
        page_num = response.meta.get('page_num')
        self.logger.info(f"Analyse de la rubrique {rubrique_id}, page {page_num}: {response.url}")
        
        # posts blocks - cluster for each articles
        post_blocks = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')
        
        # Find articles links
        post_links = post_blocks.xpath('.//a[contains(@href, "spip.php?article")]')
        post_urls = post_links.xpath('@href').getall()
        
        self.logger.info(f"Found {len(post_urls)} articles in {response.url}")
        
        for url in post_urls:
            # Convertion of  relatives URLs to absolute
            absolute_url = response.urljoin(url)
            self.logger.info(f"Article's URL found: {absolute_url}")
            yield scrapy.Request(url=absolute_url, callback=self.parse_infos)
    
    def parse_infos(self, response):
        self.logger.info(f"Extraction des informations de: {response.url}")
        rubrique_id = response.meta.get('rubrique_id')
        page_num = response.meta.get('page_num')
        
        # Title scraping
        post_title = response.xpath('//h1[@class="entry-title"]/text()').get()
        
        # post content extraction
        post_content = response.xpath('//div[contains(@class, "col-md-8")]//p/text()').getall()
        
        # Date of post extraction
        publication_date = response.xpath('//div[contains(@class, "article-meta")]//text()').get()
        if not publication_date:
            publication_date = response.xpath('//div[contains(@class, "container")]//p[contains(text(), "Publié")]/text()').get()

        # comments list
        all_comments = []
        
        # Comments section
        comments_blocks = response.xpath('//ul[@class="forum"]/li')
        
        for comment_block in comments_blocks:
            # 1. Main Comment section
            comment_div = comment_block.xpath('./div[contains(@class, "forum-message")]')
            
            # Extraction comment metadata
            #comment_author = comment_div.xpath('.//strong/text()').get()
            comment_date = comment_div.xpath('.//font/text()').get()
            
            comment_text = comment_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
            if comment_text:
                comment_text = ' '.join([text.strip() for text in comment_text if text.strip()])
            
            # 2. replies to main comment section
            replies_list = []
            
            # Indexing of replies blocks
            replies = comment_block.xpath('./ul/li')
            
            for reply in replies:
                reply_div = reply.xpath('./div[contains(@class, "forum-message")]')
                
                # Extraction des métadonnées de la réponse
                #reply_author = reply_div.xpath('.//strong/text()').get()
                reply_date = reply_div.xpath('.//font/text()').get()
                
                # Replies text extraction
                reply_text = reply_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
                if reply_text:
                    reply_text = ' '.join([text.strip() for text in reply_text if text.strip()])
                
                # Ajouter cette réponse à la liste des réponses
                replies_list.append({
                    #'author': reply_author,
                    'date': reply_date,
                    'text': reply_text
                })
            
            # Add to comment list named all_comments, the comment, its metadata, and its replies
            all_comments.append({
                #'author': comment_author,
                'date': comment_date,
                'text': comment_text,
                'replies': replies_list
            })

        # Saving
        yield {
            'title': post_title,
            'date_publication': publication_date,
            'post': post_content,
            'url': response.url,
            'rubrique_id': rubrique_id,
            'page_num': page_num,
            'comments': all_comments
        }


# Execution of our spider
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "FEEDS": {
            "results.json": {"format": "json", "encoding": "utf8"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        
        "LOG_LEVEL": "INFO",
         
        "DOWNLOAD_DELAY": 1.0,
       
        "ROBOTSTXT_OBEY": True,
       
        "DOWNLOADER_CLIENT_TLS_CIPHERS": "DEFAULT:!DH"
    })
    process.crawl(FasoNet)
    process.start()
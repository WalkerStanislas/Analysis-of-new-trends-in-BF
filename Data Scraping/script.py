import scrapy
from scrapy.crawler import CrawlerProcess

class FasoNet(scrapy.Spider):
    name = 'myspider'
    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
    }

    def start_requests(self):
        # rubriques urls (société, politique, économie, etc.)
        urls = [
            'https://lefaso.net/spip.php?rubrique4', 
            'https://lefaso.net/spip.php?rubrique2', 
            'https://lefaso.net/spip.php?rubrique3', 
            'https://lefaso.net/spip.php?rubrique62'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_post_url)

    def parse_post_url(self, response):
        # Log pour débogage
        self.logger.info(f"Analyse de la rubrique: {response.url}")
        
        # posts blocks - ciblage plus précis des conteneurs d'articles
        post_blocks = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')
        
        # Trouver les liens d'articles
        post_links = post_blocks.xpath('.//a[contains(@href, "spip.php?article")]')
        post_urls = post_links.xpath('@href').getall()
        
        self.logger.info(f"Trouvé {len(post_urls)} articles dans {response.url}")
        
        for url in post_urls:
            # Convertir les URLs relatives en URLs absolues
            absolute_url = response.urljoin(url)
            self.logger.info(f"URL d'article trouvée: {absolute_url}")
            yield scrapy.Request(url=absolute_url, callback=self.parse_infos)
    
    def parse_infos(self, response):
        self.logger.info(f"Extraction des informations de: {response.url}")
        comments = []
        
        # Extraction du titre
        post_title = response.xpath('//h1[@class="entry-title"]/text()').get()
        
        # Extraction du contenu - ciblage plus précis
        post_content = response.xpath('//div[contains(@class, "col-md-8")]//p/text()').getall()
        
        # Date de publication - ciblage plus précis
        publication_date = response.xpath('//div[contains(@class, "article-meta")]//text()').get()
        if not publication_date:
            publication_date = response.xpath('//div[contains(@class, "container")]//p[contains(text(), "Publié")]/text()').get()

        # Structure pour stocker tous les commentaires
        all_comments = []
        
        # Trouver les blocs de commentaires
        comments_blocks = response.xpath('//ul[@class="forum"]/li')
        
        for comment_block in comments_blocks:
            # Extraction des données du commentaire principal
            comment_div = comment_block.xpath('./div[contains(@class, "forum-message")]')
            
            # Extraction des métadonnées du commentaire
            #comment_author = comment_div.xpath('.//strong/text()').get()
            comment_date = comment_div.xpath('.//font/text()').get()
            
            # Correction du sélecteur pour le texte du commentaire (manque un "=" dans votre code original)
            comment_text = comment_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
            if comment_text:
                comment_text = ' '.join([text.strip() for text in comment_text if text.strip()])
            
            # Structure pour stocker les réponses à ce commentaire
            replies_list = []
            
            # Trouver les réponses à ce commentaire
            replies = comment_block.xpath('./ul/li')
            
            for reply in replies:
                reply_div = reply.xpath('./div[contains(@class, "forum-message")]')
                
                # Extraction des métadonnées de la réponse
                reply_author = reply_div.xpath('.//strong/text()').get()
                reply_date = reply_div.xpath('.//font/text()').get()
                
                # Extraction du texte de la réponse
                reply_text = reply_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
                if reply_text:
                    reply_text = ' '.join([text.strip() for text in reply_text if text.strip()])
                
                # Ajouter cette réponse à la liste des réponses
                replies_list.append({
                    'author': reply_author,
                    'date': reply_date,
                    'text': reply_text
                })
            
            # Ajouter ce commentaire et ses réponses à la liste complète
            all_comments.append({
                #'author': comment_author,
                'date': comment_date,
                'text': comment_text,
                'replies': replies_list
            })
        
        yield {
            'titre': post_title,
            'date_publication': publication_date,
            'contenu': post_content,
            'url': response.url,
            'commentaires': all_comments
        }


# Pour exécuter le spider
if __name__ == "__main__":
    process = CrawlerProcess(settings={
        "FEEDS": {
            "resultats.json": {"format": "json", "encoding": "utf8"},
        },
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "LOG_LEVEL": "INFO"
    })
    process.crawl(FasoNet)
    process.start()
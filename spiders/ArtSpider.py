from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtAuctionItem
from scrapy.contrib.spiders import CrawlSpider

class ArtSpider(BaseSpider):
        name= 'art_spider'
        allowed_domains=['sothebys.com']
        start_urls=['http://www.sothebys.com/en/auctions/2014/contemporary-curated-n09196.html#&page=all&sort=lotNum-asc&viewMode=list']



        def parse(self,response):
                art_item=ArtAuctionItem()
                hxs = HtmlXPathSelector(response)
                #paths=hxs.select("/html/body/div[@id='bodyWrap']/div[contains(concat(' ',normalize-space(@class),' '),'auctions-container sale sale-list-page')]/section[@id='lot-list']/article[contains(concat(' ',normalize-space(@class),' '),'clearfix sale-article')]")
                paths=response.selector.xpath("//div[@class='details']")
                print paths
                for path in paths:
                	print path.xpath(".//h4")
                	art_item['title']=path.xpath(".//h4[contains(concat(' ',normalize-space(@class),' '),'alt title')]/a/text()").extract()

                
                		
                return art_item
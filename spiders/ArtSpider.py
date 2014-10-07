from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtAuctionItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

class ArtSpider(CrawlSpider):
        name= 'art_spider'
        
        def __init__(self, num=None, *args, **kwargs):
                super(ArtSpider, self).__init__(*args, **kwargs)
                self.allowed_domains=['sothebys.com']

                
                self.start_urls=['http://www.sothebys.com/en/auctions/ecatalogue/2014/contemporary-curated-n09196/lot.%s.html' % num]
        

        def parse(self,response):
                art_item=ArtAuctionItem()
                hxs = HtmlXPathSelector(response)
                art_item['lower_estimate']=response.xpath("//span[@class='range-from']/text()").extract()[0]
                art_item['upper_estimate']=response.xpath("//span[@class='range-to']/text()").extract()[0]
                art_item['title']=response.xpath("//div[@class='lotdetail-subtitle']/text()").extract()[0]
                
                art_item['name']=response.xpath("//div[@class='lotdetail-guarantee']/text()").extract()[0]
                try:
                        art_item['actual_price']=response.xpath("//div[@class='price-sold']/span/@data-price").extract()[0]
                except:
                        print 'Art is not sold'
                        art_item['actual_price']=0
                return art_item
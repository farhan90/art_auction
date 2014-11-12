from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtAuctionItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http.request import Request
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
class ArtSpider(CrawlSpider):
        name= 'art_spider'
        
        def __init__(self,*args, **kwargs):
                super(ArtSpider, self).__init__(*args, **kwargs)
                self.allowed_domains=['sothebys.com']
                dispatcher.connect(self.spider_closed, signals.spider_closed)
                
                
                self.start_urls=['http://www.sothebys.com/en/auctions/results.html/']
                self.driver=webdriver.Chrome()

        def spider_closed(self, spider):
                self.driver.quit()
                
        def parse(self,response):
                self.driver.get(response.url)
                time.sleep(2)
                select =self.driver.find_element_by_xpath("//label/input[@value='/data/departments/contemporary-art']")
                self.driver.execute_script("arguments[0].click();", select)
                time.sleep(5)
                page_info=self.driver.find_element_by_class_name("page-info")
                page_nums=str(page_info.text).split(" ")
                max_val=int(page_nums[len(page_nums)-1])
                print max_val
                inputs = self.driver.find_elements_by_xpath("//a[text()='View Details']")
               
                curr_val=1
                
                links=[]
                

                while curr_val<max_val:
                        time.sleep(1)
                        inputs = self.driver.find_elements_by_xpath("//a[text()='View Details']") 
                        for i in inputs:
                                link=i.get_attribute("href")
                                if(link!=None):
                                        links.append(link)
                        self.driver.find_element_by_css_selector("a.btn.btn-link.next").click()
                        time.sleep(3)
                        page_info=self.driver.find_element_by_class_name("page-info")
                        page_nums=str(page_info.text).split(" ")
                        curr_val=int(page_nums[len(page_nums)-3])
                        print(curr_val)

                print("The length of the list with duplicates" + str(len(links)))        
                links=list(set(links))
                print("The length of the list without duplicates" + str(len(links))) 
                #yield Request(url=links[0],callback=self.parse_page)
                for link in links:
                        print(link)
                        yield Request(url=link,callback=self.parse_page)




        def parse_page(self,response):
                local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)
                local_driver.get(response.url)
                time.sleep(2)
                page_info=local_driver.find_element_by_class_name("page-info")
                page_nums=str(page_info.text).split(" ")
                max_val=int(page_nums[len(page_nums)-1])
                print max_val
                inputs = local_driver.find_elements_by_xpath("//div[@class='details']/h4/a") 
                curr_val=1
                links=[]
                while curr_val<max_val:
                        time.sleep(1)
                        inputs = local_driver.find_elements_by_xpath("//div[@class='details']/h4/a") 
                        for i in inputs:
                                link=i.get_attribute("href")
                                if(link!=None):
                                        links.append(link)
                                
                        self.driver.find_element_by_css_selector("a.btn.btn-link.next").click()
                        time.sleep(3)
                        page_info=self.driver.find_element_by_class_name("page-info")
                        page_nums=str(page_info.text).split(" ")
                        curr_val=int(page_nums[len(page_nums)-3])
                        print(curr_val)

                local_driver.quit()

                links=list(set(links))
                for link in links:
                       print link
                       yield Request(url=link,callback=self.parse_item)


        def parse_item(self,response):        
                art_item=ArtAuctionItem()
                hxs = HtmlXPathSelector(response)
                art_item['currency']=response.xpath("//div[contains(concat(' ', normalize-space(@class), ' '),' dropdown currency-dropdown inline ')]/@data-default-currency").extract()[0]
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

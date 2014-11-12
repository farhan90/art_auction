from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtInfoItem
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
        name= 'art_info'
        
        def __init__(self,*args, **kwargs):
                super(ArtSpider, self).__init__(*args, **kwargs)
                self.allowed_domains=['findartinfo.com']
                dispatcher.connect(self.spider_closed, signals.spider_closed)
                
                
                self.start_urls=['http://www.findartinfo.com/browse-by-artist.html']
                self.driver=webdriver.Chrome()


        def spider_closed(self, spider):
                self.driver.quit()


        def parse(self,response):
        	self.driver.get(response.url)
        	time.sleep(2)
        	inputs=self.driver.find_elements_by_xpath("//center/span/a") 

        	links=[]
        	for i in inputs:
        		link=i.get_attribute('href')
        		if(link!=None):
        			links.append(link)

        	links.append('http://www.findartinfo.com/A/browse-by-artist.html')
        	
                links=list(set(links))

        	for link in links:
        		yield Request(url=link,callback=self.parse_each_letter)

                #yield Request(url=links[0],callback=self.parse_each_letter)
        		



        def parse_each_letter(self,response):
        	local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
        	local_driver.get(response.url)
        	time.sleep(2)
        	
        	links=[]
        	page_info=local_driver.find_elements_by_xpath("//p[@align='right']/b")
        	page_info_first=page_info[0]
        	page_nums=str(page_info_first.text).split(" ")
        	max_val=int(page_nums[len(page_nums)-1])
        	#print(max_val)

        	curr_val=1

        	while curr_val<max_val:
        		inputs = local_driver.find_elements_by_xpath("//span[@class='linkgoogle']/a")
        		#print(curr_val)
        		for i in inputs:
        			link=i.get_attribute('href')
        			if(link!=None):
        				links.append(link)

        		

        		local_driver.find_element_by_link_text('>').click()
        		page_info=local_driver.find_elements_by_xpath("//p[@align='right']/b")
        		page_info_first=page_info[0]
        		page_nums=str(page_info_first.text).split(" ")
        		curr_val=int(page_nums[len(page_nums)-3])
                local_driver.quit()

                links=list(set(links))
        	for link in links:
        		yield Request(url=link,callback=self.parse_data)


                #yield Request(url='http://www.findartinfo.com/list-prices-by-artist/202157/max.html',callback=self.parse_data)

        def parse_data(self,response):

                page_list=str(response.xpath("//h2/text()")[0].extract()).split("|")
                curr_val=int(page_list[2].split(" ")[4])
                max_val=int(page_list[2].split(" ")[6])

                if(curr_val>max_val):
                        return

                

                print(curr_val)
                print(max_val)

                table_rows=response.xpath("//tr[@onmouseover]")

                top_data=response.xpath("//table[@style='margin-top:5px']/tr")
                birth=str(top_data[0].xpath("td/text()").extract()[0]).strip()
                death=str(top_data[1].xpath("td/text()").extract()[0]).strip()
                artist_name=str(response.xpath("//h1[@class='underline']/text()").extract()).split(" ")[20:]

                items=[]


                
                local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
                local_driver.get(response.url)
                curr_val=0;
                while max_val>curr_val:
                        curr_val=curr_val+1
                        print("now curr_val "+str(curr_val))
                        table_rows=local_driver.find_elements_by_xpath("//tr[@onmouseover]")            
                        for row in table_rows:
                                art_item=ArtInfoItem()
                                cols=row.find_elements_by_xpath("td")
                                art_item['date']=str(cols[1].text).strip()
                                art_item['title']=cols[2].find_element_by_xpath("span/a").text
                                art_item['size']=cols[3].find_element_by_xpath("span").text
                                art_item['medium']=str(cols[4].text).strip()
                                art_item['actual_price']=str(cols[5].text).strip()
                                art_item['name']=artist_name
                                art_item['birth']=birth
                                art_item['death']=death
                                
                                items.append(art_item)

                        if(curr_val<max_val):
                                print('I am clicking')
                                local_driver.find_element_by_link_text('>').click()
                                time.sleep(2)
                                
                        


                local_driver.quit()
                items=sorted(set(items))
                return items











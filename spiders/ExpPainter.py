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
import re



class ArtSpider(CrawlSpider):
	name= 'exp_art'
	
	def __init__(self,s_url,*args,**kwargs):
		super(ArtSpider, self).__init__(*args, **kwargs)
		self.allowed_domains=['findartinfo.com']
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		
		
		self.start_urls=[s_url]
		#self.driver=webdriver.Chrome()


	def spider_closed(self, spider):
		#self.driver.quit()
		pass


	def parse(self,response):
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
		x=" ".join(artist_name)
		match_obj=re.match('(.*[^\'\]])',x)
		artist_name=match_obj.group(1)

		items=[]


		
		#local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)
		local_driver=webdriver.Chrome()
		local_driver.get(response.url)

		match_obj=re.match('(.*page_)',response.url)
		new_url=match_obj.group(1)

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
				temp_price=str(cols[5].text).strip()
				art_item['name']=artist_name
				art_item['birth']=birth
				art_item['death']=death

				match_obj=re.match('([^a-zA-Z]*)',temp_price)
				if match_obj.group(1)!='':
					actual_price=int(match_obj.group(1).replace(',',''))
				else:
					actual_price=0
				
				if(actual_price<100000):
					print("in the if")
					local_driver.quit()
					items=sorted(set(items))
					return items
				else:
					art_item['actual_price']=actual_price
					items.append(art_item)

			if(curr_val<max_val):
				print('I am clicking')
				local_driver.get(new_url+str(curr_val)+'.html')
				time.sleep(2)
				
			


		local_driver.quit()
		items=sorted(set(items))
		return items











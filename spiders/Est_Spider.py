from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtEstItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http.request import Request
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException



class ArtSpider(CrawlSpider):
	name= 'est_art'
	
	def __init__(self,*args,**kwargs):
		super(ArtSpider, self).__init__(*args, **kwargs)
		self.allowed_domains=['findartinfo.com']
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		
		
		self.start_urls=['http://www.sothebys.com/en/search.html?ex_currency=USD&startDate=01%2F06%2F2013&endDate=24%2F12%2F2013&ex_saleTitle=Contemporary*&ex_soldPR=soldPR#keywords=']
		self.driver=webdriver.Chrome()


	def spider_closed(self, spider):
		self.driver.quit()
		pass


	def parse(self,response):
		self.driver.get(response.url)
		time.sleep(10)
		i=1
		art_items=[]
		max_val=int(self.driver.find_element_by_class_name("total").text)
		print max_val
		curr_val=0
		while curr_val<=max_val:
			curr_val= int (self.driver.find_element_by_class_name("items").text.split("-")[1])
			table_rows=self.driver.find_elements_by_xpath('//tr[@valign="top"]')
			for row in table_rows:
				artist_name_list=row.find_elements_by_xpath('./td[@class="column3"]/div[@class="artist"]/a')
				artist_name=""
				if len(artist_name_list)>0:
					artist_name=artist_name_list[0].text

				title_list=row.find_elements_by_xpath('./td[@class="column3"]/div[@class="workTitle"]/a')
				title=""
				if len(title_list)!=0:
					title=title_list[0].text


				actual_price_curr=row.find_elements_by_xpath('./td[@class="column5"]/div[@class="salePrice"]/div')
				actual_price=""+str(0)
				currency=""
				if len(actual_price_curr)>0:
					price_n_curr=actual_price_curr[0].text.split(" ")
					actual_price=price_n_curr[0]
					currency=price_n_curr[1]


				estimates=row.find_elements_by_xpath('./td[@class="column5"]/div[@class="estimate"]/div')
				upper_estimate=""+str(0)
				lower_estimate=""+str(0)
				if len(estimates)>0:
					est=estimates[0].text.split("-")
					if len(est)>=2:
						upper_estimate_temp=est[1]
						upper_estimate=upper_estimate_temp.split(" ")[1]
						lower_estimate=est[0]


				date=row.find_elements_by_xpath('./td[@class="column4"]/div[@class="locationDate"]')[1]
				print (artist_name.encode("UTF-8"),actual_price,str(curr_val))

				art_item=ArtEstItem()
				art_item['name']=artist_name.encode("UTF-8")
				art_item['title']=title
				art_item['upper_estimate']=upper_estimate
				art_item['lower_estimate']=lower_estimate
				art_item['currency']=currency
				art_item['date']=date.text
				art_item['actual_price']=actual_price

				art_items.append(art_item)

			i=i+1

			pages=self.driver.find_elements_by_xpath('//span[@class="page"]')
			to_click=0
			for page in pages:
				if page.text != '':
					page_num=int(page.text)
					if(page_num==i):
						to_click=1
						break


			if to_click!=0:
				page.click()

			else:
				break
			price_val=self.driver.find_elements_by_xpath('//tr[@valign="top"]/td[@class="column5"]/div[@class="salePrice"]/div')[0]

			my_bool=0
			while True:
				try:
					if price_val.text=="":
						print("Wtf :" +price_val.text)
						price_val=self.driver.find_elements_by_xpath('//tr[@valign="top"]/td[@class="column5"]/div[@class="salePrice"]/div')[0]
						time.sleep(2)
					else:
						print(price_val.text)
						break
				except StaleElementReferenceException:
					print("Got an except")
					price_val=self.driver.find_elements_by_xpath('//tr[@valign="top"]/td[@class="column5"]/div[@class="salePrice"]/div')[0]
					continue

		return art_items
			
				


		
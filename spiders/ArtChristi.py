from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from art_auction.items import ArtChristieItem
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http.request import Request
from selenium import webdriver
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import Select


class ArtSpider(CrawlSpider):
		name= 'art_christi'
		
		def __init__(self,*args, **kwargs):
				super(ArtSpider, self).__init__(*args, **kwargs)
				self.allowed_domains=['christies.com']
				dispatcher.connect(self.spider_closed, signals.spider_closed)
				
				
				self.start_urls=['http://www.christies.com/results/index.aspx?month=11&year=2014&locations=&scids=7&pg=1&action=&initialpageload=false']
				self.driver=webdriver.Chrome()


		def spider_closed(self, spider):
				self.driver.quit()


		def parse(self,response):
			self.driver.get(response.url)
			time.sleep(2)

			inputs=self.driver.find_elements_by_xpath("//div[@id='results_nav_by_year']/a")

			links=[]
			for i in inputs:
				link=i.get_attribute('href')
				if(link!=None):
					links.append(link)

			for link in links:
				yield Request(url=link,callback=self.parse_page)

			#yield Request(url=links[1],callback=self.parse_page)


		def parse_page(self,response):
			local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
			local_driver.get(response.url)
			
			time.sleep(2)
			inputs=local_driver.find_elements_by_xpath("//div[@class='auction-info']/p[@class='description']/a")


			links=[]
			for i in inputs:
				link=i.get_attribute('href')
				if(link!=None):
					links.append(link)

			for link in links:
				yield Request(url=link,callback=self.parse_go_to_page)

			#yield Request(url='http://www.christies.com/The-Ski-Sale-Travel-24090.aspx',callback=self.parse_go_to_page)



		def parse_go_to_page(self,response):
			#local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
			local_driver=webdriver.Remote(desired_capabilities={'browserName': 'htmlunit', 'javascriptEnabled': False, 'platform': 'ANY', 'version': '', 'setThrowExceptionOnScriptError': False})
			local_driver.get(response.url)
			time.sleep(2)

			local_driver.find_element_by_link_text('View Results').click()
			time.sleep(2)

			lot_num_data=local_driver.find_elements_by_xpath("//strong[@class='chr-search-lot-results']")[0].text

			print(lot_num_data)

			split_lot_num_data=lot_num_data.split(" ")
			max_val=int(split_lot_num_data[5])
			curr_val=int(split_lot_num_data[3])

			print("The max num is "+str(max_val))
			print("The curr val is "+str(curr_val))

			links=[]
			while curr_val<max_val:
				inputs=local_driver.find_elements_by_xpath("//h3[@class='chr-result-hd']/a")
				for i in inputs:
					link=i.get_attribute('href')
					if(link!=None):
						links.append(link)

				local_driver.find_element_by_css_selector(".icon.ir.chr-pager-next.chr-pager-link").click()
				lot_num_data=local_driver.find_elements_by_xpath("//strong[@class='chr-search-lot-results']")[0].text
				split_lot_num_data=lot_num_data.split(" ")
				curr_val=int(split_lot_num_data[3])
				print(curr_val)

			for link in links:
				yield Request(url=link,callback=self.parse_data)

			#yield Request(url='http://www.christies.com/lotfinder/posters-signage-advertising/jules-abel-faivre-sports-dhiver-chamonix-5648748-details.aspx?from=salesummary&intObjectID=5648748&sid=3216db3b-9e79-4827-8202-50cc56f15da2',callback=self.parse_data)


		def parse_data(self,response):
			local_driver=webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
			local_driver.get(response.url)

			name=local_driver.find_elements_by_xpath("//div[@class='details-content-header']/h1")[0].text
			title=local_driver.find_elements_by_xpath("//div[@class='details-content-header']/h2")[0].text
			date=local_driver.find_element_by_css_selector(".info-item.date").text
			actual_price=local_driver.find_element_by_css_selector(".sublist-item").text
			price=actual_price.split(" ")[0]
			estimate=local_driver.find_elements_by_xpath("//div[contains(concat(' ', normalize-space(@class), ' '),' wrapper estimate-wrapper ')]/ul/li")[0]
			new_estimate=estimate.text
			data=new_estimate.split(" ")
			lower_estimate=str(data[0])
			upper_estimate=str(data[2])

			item=ArtChristieItem()

			item['name']=name
			item['title']=title
			item['date']=date
			item['actual_price']=price
			item['upper_estimate']=upper_estimate
			item['lower_estimate']=lower_estimate

			return item

			# print(name)
			# print(title)
			# print(date)
			# print(price)
			# print(upper_estimate)
			# print(lower_estimate)








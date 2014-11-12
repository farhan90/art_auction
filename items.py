# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#import scrapy
from scrapy.item import Item, Field

class ArtAuctionItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title=Field()
    name= Field()
    upper_estimate=Field()
    lower_estimate=Field()
    actual_price=Field()
    currency=Field()
    pass

class ArtInfoItem(Item):
	actual_price=Field()
	date=Field()
	size=Field()
	medium=Field()
	title=Field()
	name=Field()
	birth=Field()
	death=Field()
	pass

class ArtChristieItem(Item):
	actual_price=Field()
	upper_estimate=Field()
	lower_estimate=Field()
	date=Field()
	name=Field()
	title=Field()	


# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AnycrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class AitaotuItems(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    ref_url = scrapy.Field()
    img_url = scrapy.Field()
    

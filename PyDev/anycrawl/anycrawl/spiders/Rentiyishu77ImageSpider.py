# -*- coding: utf-8 -*-
import scrapy

from scrapy import Request
from scrapy import signals
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.spider import CrawlSpider, Rule
from scrapy.xlib.pydispatch import dispatcher
from lxml import etree

from anycrawl.items import AitaotuItems
'''
import logging
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
'''

class MultSetSpider(CrawlSpider):
    name = "rentiyishu77Spider"
    allowed_domains = ["rentiyishu77.org"]
    start_urls = [
        "http://www.rentiyishu77.org/shineirenti/"
        ]

    def __init__(self):
        dispatcher.connect(self.spider_opened,signals.spider_opened)
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def parse(self, response):
        base_url = get_base_url(response)
        yield Request(base_url, callback=self.parse_page_lvl1, dont_filter=False)
        
    def parse_page_lvl1(self,response):
        items = []
        base_url = get_base_url(response)

        links = response.xpath('//ul[@class="photo"]//a').extract()
        for index, link in enumerate(links):
            selector = etree.HTML(link)
            
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]
            
            titles = selector.xpath('///text()')
            if len(titles) == 0:
                title = '未知网页标题'
            else:
                title = titles[0]
            
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            item = AitaotuItems()
            item['url'] = abs_url
            item['ref_url'] = abs_url
            item['title'] = title
            items.append(item)
        
        #for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
        #    abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
        #    yield Request(abs_url, callback=self.parse_page_lvl1, dont_filter=False)
        
        for item in items:
            #print(item['title'])
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_page_lvl2, dont_filter=False)

        if len(response.xpath("//a[text()='下一页']")) > 0:
            next_label = response.xpath("//a[text()='下一页']").extract()[0]
            selector = etree.HTML(next_label)
            url_next = selector.xpath('//a/@href')[0]
            abs_url = str(urljoin_rfc(base_url, url_next), encoding = "utf-8")
            yield Request(abs_url, callback=self.parse_page_lvl1, dont_filter=False)

    def parse_page_lvl2(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
        
        for img_url in response.xpath('//div[@class="lm"]//img/@src').extract():
            item = AitaotuItems()
            item['ref_url'] = g_item['ref_url']
            item['title'] = g_item['title']
            img_url = img_url.strip()
            item['img_url'] = img_url
            #print(img_url)
            yield item

        if len(response.xpath("//a[text()='下一页']")) > 0:
            next_label = response.xpath("//a[text()='下一页']").extract()[0]
            selector = etree.HTML(next_label)
            url_next = selector.xpath('//a/@href')[0]
            abs_url = str(urljoin_rfc(base_url, url_next), encoding = "utf-8")
            yield Request(abs_url, meta={'g_item': g_item}, callback=self.parse_page_lvl2, dont_filter=False)
            
    def spider_opened(self,spider):
        print("★★★★★task start!★★★★★")

    def spider_closed(self,spider):
        print("★★★★★task over!★★★★★")
            
class OneSetSpider(CrawlSpider):
    name = "rentiyishu77Spider1"
    allowed_domains = ["rentiyishu77.org"]
    start_urls = [
        "http://www.rentiyishu77.org/shineirenti/201711/14015.html"
        ]

    def __init__(self):
        dispatcher.connect(self.spider_opened,signals.spider_opened)
        dispatcher.connect(self.spider_closed,signals.spider_closed)

    def parse(self, response):
        base_url = get_base_url(response)
        titles = response.xpath('//title/text()').extract()
        if len(titles) == 0:
            title = '未知网页标题'
        else:
            title = titles[0]
        item = AitaotuItems()
        item['ref_url'] = base_url
        item['title'] = title
        yield Request(base_url, meta={'g_item': item}, callback=self.parse_page_lvl1, dont_filter=False)
        
    def parse_page_lvl1(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)

        for img_url in response.xpath('//div[@class="lm"]//img/@src').extract():
            item = AitaotuItems()
            item['ref_url'] = g_item['ref_url']
            item['title'] = g_item['title']
            img_url = img_url.strip()
            item['img_url'] = img_url
            #print(img_url)
            yield item
        
        if len(response.xpath("//a[text()='下一页']")) > 0:
            next_label = response.xpath("//a[text()='下一页']").extract()[0]
            selector = etree.HTML(next_label)
            url_next = selector.xpath('//a/@href')[0]
            abs_url = str(urljoin_rfc(base_url, url_next), encoding = "utf-8")
            yield Request(abs_url, meta={'g_item': item}, callback=self.parse_page_lvl1, dont_filter=False)

    def spider_opened(self,spider):
        print("★★★★★" + self.name + " task start!★★★★★")

    def spider_closed(self,spider):
        print("★★★★★" + self.name + " task end!★★★★★")
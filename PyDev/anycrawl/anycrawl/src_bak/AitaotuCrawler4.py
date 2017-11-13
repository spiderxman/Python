# -*- coding: utf-8 -*-
import scrapy
from anycrawl.items import AitaotuItems

from scrapy.http import Request
from scrapy import Request
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from lxml import etree
'''
import logging
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
'''

class AitaotuCrawler(scrapy.Spider):
    name = "aitaotuCrawler4"
    allowed_domains = ["aitaotu.com"]
    start_urls = [
        "https://www.aitaotu.com/tag/huayan.html",
        "https://www.aitaotu.com/tag/jiamiannvhuang.html",
        "https://www.aitaotu.com/tag/xiweisha.html",
        "https://www.aitaotu.com/tag/simeivip.html",
        "https://www.aitaotu.com/tag/maomengbang.html",
        "https://www.aitaotu.com/tag/yingsihui.html",
        '''
        "https://www.aitaotu.com/tag/youmihui.html",
        "https://www.aitaotu.com/tag/xingleyuan.html",
        "https://www.aitaotu.com/tag/feituwang.html",
        "https://www.aitaotu.com/tag/meixiu.html",
        "https://www.aitaotu.com/tag/shanghaixuancai.html",
        "https://www.aitaotu.com/tag/chizuzhe.html",
        "https://www.aitaotu.com/tag/aixiu.html",
        "https://www.aitaotu.com/tag/ruyixiezhen.html",
        "https://www.aitaotu.com/tag/aimishe.html",
        "https://www.aitaotu.com/tag/meituibaobei.html",
        '''
        ]

    def parse(self, response):
        base_url = get_base_url(response)
        yield Request(base_url, callback=self.parse_page_lvl1, dont_filter=False)
        
    def parse_page_lvl1(self,response):
        items_1 = []
        base_url = get_base_url(response)

        links = response.xpath('//div[@id="mainbody"]//a').extract()
        for index, link in enumerate(links):
            selector = etree.HTML(link)
            
            urls = selector.xpath('//a/@href')
            if len(urls) == 0:
                continue
            url = urls[0]
            
            titles = selector.xpath('//a/@title')
            if len(titles) == 0:
                title = ''
            title = titles[0]
            
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            item = AitaotuItems()
            item['url'] = abs_url
            item['ref_url'] = abs_url
            item['title'] = title
            items_1.append(item)
        
        for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            yield Request(abs_url, callback=self.parse_page_lvl1, dont_filter=False)
        
        for item in items_1:
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_page_lvl2, dont_filter=False)
            
    def parse_page_lvl2(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
            
        for url in response.xpath('//div[@class="pages"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            
            for img_url in response.xpath('//div[@id="big-pic"]//img/@src').extract():
                item = AitaotuItems()
                item['ref_url'] = g_item['ref_url']
                item['title'] = g_item['title']
                item['img_url'] = img_url
                yield item

            yield Request(abs_url, meta={'g_item': g_item}, callback=self.parse_page_lvl2, dont_filter=False)
   
        
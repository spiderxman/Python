# -*- coding: utf-8 -*-
import scrapy
from anycrawl.items import AitaotuItems
import logging

from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from scrapy import Request
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from lxml import etree

class AitaotuCrawler(scrapy.Spider):
    name = "aitaotuCrawler3"
    allowed_domains = ["aitaotu.com"]
    start_urls = ["https://www.aitaotu.com/tag/chizuzhe.html"]
    visited = []

    def parse(self, response):
        base_url = get_base_url(response)
        yield Request(base_url, callback=self.parse_page_lvl1)
        
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
            if abs_url in self.visited:
                continue
            self.visited.append(abs_url)
            item = AitaotuItems()
            item['url'] = abs_url
            item['ref_url'] = abs_url
            item['title'] = title
            items_1.append(item)
        
        for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print(abs_url)
            self.visited.append(abs_url)

            yield Request(abs_url, callback=self.parse_page_lvl1)
        
        for item in items_1:
            yield Request(url=item['url'], meta={'g_item': item}, callback=self.parse_page_lvl2)
            
    def parse_page_lvl2(self,response):
        g_item = response.meta['g_item']
        base_url = get_base_url(response)
            
        for url in response.xpath('//div[@class="pages"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            self.visited.append(abs_url)
            
            for img_url in response.xpath('//div[@id="big-pic"]//img/@src').extract():
                if img_url in self.visited:
                    continue
                self.visited.append(img_url)
                item = AitaotuItems()
                item['ref_url'] = g_item['ref_url']
                item['title'] = g_item['title']
                item['img_url'] = img_url
                yield item

            yield Request(abs_url, meta={'g_item': g_item}, callback=self.parse_page_lvl2)
   
        
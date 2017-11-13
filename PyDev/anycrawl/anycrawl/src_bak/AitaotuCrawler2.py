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

class AitaotuCrawler(scrapy.Spider):
    name = "aitaotuCrawler2"
    allowed_domains = ["aitaotu.com"]
    start_urls = ["https://www.aitaotu.com/tag/chizuzhe.html"]
    visited = []
    img_urls = []

    def parse(self, response):

        base_url = get_base_url(response)
        '''
        item['url'] = response.url
        item['name'] = response.xpath(u"//title")
        for url in response.xpath('//div[@class="pages"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            print("sencond pages:"+abs_url)
            self.visited.append(abs_url)
            yield Request(abs_url, callback=self.get_img_url)
        #item['img_urls'] = self.img_urls
        #yield item
        
        for url in response.xpath('//div[@id="mainbody"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print(abs_url)
            self.visited.append(abs_url)
            print(self.img_urls)
            
            item['img_urls'] = self.img_urls
            yield item
            yield Request(abs_url, callback=self.parse)

        for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print(abs_url)
            self.visited.append(abs_url)

            yield Request(abs_url, callback=self.parse)
        '''
        yield Request(base_url, callback=self.parse_main_page)
        
    def parse_main_page(self,response):
        items_1 = []
        base_url = get_base_url(response)
        
        for url in response.xpath('//div[@id="mainbody"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print(abs_url)
            self.visited.append(abs_url)
            item = AitaotuItems()
            #print(self.img_urls)
            
            item['url'] = abs_url
            items_1.append(item)
        
        for url in response.xpath('//div[@id="pageNum"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print(abs_url)
            self.visited.append(abs_url)

            yield Request(abs_url, callback=self.parse_main_page)
        
        for item in items_1:
            img_urls = []
            #yield item
            #yield Request(abs_url, callback=self.parse_main_page)
            #print('★' + item['url'])
            #yield Request(url=item['url'], meta={'title': item['title']}, callback=self.parse_second_page)
            #self.img_urls.clear()
            yield Request(url=item['url'], meta={'img_urls': img_urls}, callback=self.parse_second_page)
            print(img_urls)
            
    def parse_second_page(self,response):
        img_urls = response.meta['img_urls']
        #img_urls = []
        items_2 = []
        base_url = get_base_url(response)

        for img_url in response.xpath('//div[@id="big-pic"]//img/@src').extract():
            if img_url in self.visited:
                continue
            
            self.visited.append(img_url)
            #self.img_urls.append(img_url)
            #item = AitaotuItems()
            #item['img_url'] = img_url
            #item['refer_url'] = response.url
            #items_2.append(item)
            #yield item
            img_urls.append(img_url)
            
        #print('★' + response.url)
        for url in response.xpath('//div[@class="pages"]//a/@href').extract():
            abs_url = str(urljoin_rfc(base_url, url), encoding = "utf-8")
            if abs_url in self.visited:
                continue
            #print("sencond pages:"+abs_url)
            self.visited.append(abs_url)
            #img_urls = Request(abs_url, callback=self.get_img_url)
            #img_urls.append(abs_url)
            yield Request(abs_url, meta={'img_urls': img_urls}, callback=self.parse_second_page)
        
        #img_urls = []
        #for item in items_2:
            #yield item
            #yield Request(abs_url, callback=self.parse_main_page)
            #print('★' + item['url'])
            #yield Request(url=item['url'], meta={'title': item['title']}, callback=self.parse_second_page)
            #self.img_urls.clear()
            #img_urls.append(item['img_url'])
            #print("★★★" + item['img_url'])
            #yield Request(url=item['img_url'], callback=self.parse_detail_page)
        pass
    
    def parse_detail_page(self,response):
        pass
        
    def get_img_url(self,response):
        #img_urls = []
        for img_url in response.xpath('//div[@id="big-pic"]//img/@src').extract():
            if img_url in self.visited:
                continue
            
            self.visited.append(img_url)
            #self.img_urls.append(img_url)
            self.img_urls.append(img_url)
            #item = AitaotuItems()
            #return img_urls
            print("★★★")
            print(self.img_urls)
        
        
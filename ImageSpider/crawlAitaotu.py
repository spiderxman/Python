#!/usr/bin/env Python
# coding=utf-8

import os
import time
import re
import chardet
import difflib
from urllib import request
from urllib import parse
from posixpath import normpath
from lxml import etree

n = 0
path = ""
folder_create_flg = True
class MyCrawler:

    def __init__(self,seeds):
        #初始化当前抓取的深度
        #self.current_deepth = 1
        #使用种子初始化url队列
        self.linkQuence=linkQuence()
        if isinstance(seeds,str):
            self.linkQuence.addUnvisitedUrl(seeds)
        if isinstance(seeds,list):
            for seed in seeds:
                self.linkQuence.addUnvisitedUrl(seed)
        print ("Add the seeds to the unvisited url list:" + str(self.linkQuence.unVisited))
        
    def crawling(self,seeds,crawl_deepth):

        main_page_links = self.get_page_urls("pagenum")
        self.crawl_page_urls(main_page_links)
        
    def get_page_urls(self,key):
        urls = []
        #循环条件：待抓取的链接不空
        while not self.linkQuence.unVisitedUrlsEnmpy():
            #队头url出队列
            visitUrl=self.linkQuence.unVisitedUrlDeQuence()
            if visitUrl is None or visitUrl=="":
                continue
            print("Pop out one url from unvisited url list:" + visitUrl)
            #获取超链接
            links=self.getPagesHyperLinks(visitUrl,key)
            #将url放入已访问的url中
            self.linkQuence.addVisitedUrl(visitUrl)
            urls.append(visitUrl)
            #print("Visited deepth: "+str(self.current_deepth))
            #未访问的url入列
            for link in links:
                if link not in self.linkQuence.visted:
                    self.linkQuence.addUnvisitedUrl(link)
                    urls.append(link)
        return urls
     
    def crawl_page_urls(self, main_page_links):
        page_urls = []
        target_urls = []
        for main_page_link in main_page_links:
            page_urls.clear()
            links=self.getPagesHyperLinks(main_page_link,"mainbody")
            self.linkQuence.addVisitedUrl(main_page_link)
            for link in links:
                if link not in self.linkQuence.visted:
                    page_urls.append(link)
            
            for page_url in page_urls:
                global n,folder_create_flg
                n = 0;
                folder_create_flg = True
                target_urls.clear()
                self.linkQuence.addUnvisitedUrl(page_url)
                target_urls = self.get_page_urls("pages")
                for target_url in target_urls:
                    self.get_target(target_url)

    def get_target(self,url):
        page = self.get_PageHtml(url)
        if page is None:
            return None
        global n,path,folder_create_flg
        if folder_create_flg == True:
            title = self.get_html_title(page)
            path = savedir + "\\" + self.normalize_dir(title)
            self.mkDir(path)
            folder_create_flg = False
            
        target_list=page.xpath('//div[@id="big-pic"]//img/@src')

        for target in target_list:
            n+=1
            try:
                request.urlretrieve(target, path + '/%s.jpg' % n)
            except:
                ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print(ymdhms + "错误:下载失败" + target)
        
    def getPagesHyperLinks(self,url,key):
        url_list = []
        
        page = self.get_PageHtml(url)
        if page is None:
            return url_list
        #此处根据网页不同手动修正适配
        if key == "pagenum":
            #pagelist=page.xpath('//td[@id="pagelist"]/a')
            pagelist=page.xpath('//div[@id="pagenum"]//a')
        elif key == "mainbody":
            pagelist=page.xpath('//div[@id="mainbody"]//a')
        elif key == "pages":
            pagelist=page.xpath('//div[@class="pages"]//a')

        for href in pagelist:
            try:
                ret = href.get("href")
            except:
                ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print(ymdhms + "错误:可能不是一个有效的href属性")
                continue
            #整理页面上的链接，相对url变换绝对url
            ret = self.join_sub_url(url, ret)
            url_list.append(ret)

        return url_list

    #获取网页源码
    def get_PageHtml(self,url):
        #time.sleep(1)
        try:
            res = request.urlopen(url)
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + "链接打开失败:" + url)
            return None
        try:
            html = res.read()
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + "链接读取错误:" + url)
            return None
        try:
            page = etree.HTML(self.utf8_transfer(html).lower())
            #html = utf8_transfer(html)
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + "网页编码转换错误:" + url)
            return None
        return page
    
    #utf8编码转换
    def utf8_transfer(self,html):
        try:
            charset = chardet.detect(html)['encoding']
            #print(r"★★★★★网页编码形式★★★★★" + charset)
            if chardet.detect(html)['encoding'].lower() == 'gb2312':
                html = html.decode("gb2312", 'ignore')
            elif chardet.detect(html)['encoding'].lower() == 'utf-8':
                html = html.decode('utf-8', 'ignore')
            elif chardet.detect(html)['encoding'].lower() == 'gbk':
                html = html.decode('gbk', 'ignore')
        except:
            raise Exception("utf8_transfer")
        return html
    
    #组装子网页url
    def join_sub_url(self,base,url):
        try:
            url = parse.urljoin(base, url)
            arr = parse.urlparse(url)
            path = normpath(arr[2])
            if arr[2] == ".":
                path = ""
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            #print(ymdhms + r"url拼接错误:",img_url)
            return None

        return parse.urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

    #用re抽取网页Title
    def get_html_title(self,page):
        titles = page.xpath(u"//title")
        if titles is None or len(titles) == 0:
            title = ''
        else:
            title = titles[0].text
        return title

    #过滤创建文件夹非法字符
    def normalize_dir(self,s):
        s = s.replace('\\','')
        s = s.replace('/','')
        s = s.replace(':','')
        s = s.replace('*','')
        s = s.replace('?','')
        s = s.replace('"','')
        s = s.replace('<','')
        s = s.replace('>','')
        s = s.replace('|','')
        return s
    
    #创建文件夹
    def mkDir(self,path):
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            #print(path + 'is already Exists')
            return False

class linkQuence:
    def __init__(self):
        #已访问的url集合
        self.visted=[]
        #待访问的url集合
        self.unVisited=[]
    #获取访问过的url队列
    def getVisitedUrl(self):
        return self.visted
    #获取未访问的url队列
    def getUnvisitedUrl(self):
        return self.unVisited
    #设置未访问的url队列
    def setUnvisitedUrl(self, unVisited):
        self.unVisited = unVisited
    #添加到访问过得url队列中
    def addVisitedUrl(self,url):
        self.visted.append(url)
    #移除访问过得url
    def removeVisitedUrl(self,url):
        self.visted.remove(url)
    #未访问过得url出队列
    def unVisitedUrlDeQuence(self):
        try:
            return self.unVisited.pop()
        except:
            return None
    #保证每个url只被访问一次
    def addUnvisitedUrl(self,url):
        if url!="" and url not in self.visted and url not in self.unVisited:
            self.unVisited.insert(0,url)
    #获得已访问的url数目
    def getVisitedUrlCount(self):
        return len(self.visted)
    #获得未访问的url数目
    def getUnvistedUrlCount(self):
        return len(self.unVisited)
    #判断未访问的url队列是否为空
    def unVisitedUrlsEnmpy(self):
        return len(self.unVisited)==0
    
#创建保存目录
def create_savedir():
    global savedir
    ymd = time.strftime("%Y%m%d", time.localtime())
    savedir = ".\\" + ymd

def main(seeds,crawl_deepth):
    create_savedir()
    craw=MyCrawler(seeds)
    craw.crawling(seeds,crawl_deepth)

if __name__=="__main__":
    main("https://www.aitaotu.com/tag/ligui.html",10)
    print("TASK OVER!!!")

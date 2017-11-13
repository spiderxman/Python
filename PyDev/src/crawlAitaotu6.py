#!/usr/bin/env Python
# coding=utf-8

import os
import time
import chardet
from urllib import request
from urllib import parse
from posixpath import normpath
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import threading

visted=[]
unVisited=[]
mutex = threading.RLock()

class MyCrawler:
    n = 0
    folder_create_flg = True
    path = ""

    def __init__(self):
        pass
        
    def init1(self,seeds):
        #使用种子初始化url队列
        if isinstance(seeds,str):
            if seeds!="" and seeds not in visted and seeds not in unVisited:
                unVisited.insert(0,seeds)
        if isinstance(seeds,list):
            for seed in seeds:
                if seed!="" and seed not in visted and seed not in unVisited:
                    unVisited.insert(0,seed)
    
    def crawling(self,url):
        #urls = self.get_urls("pagenum","mainbody")
        if url not in visted:
            self.n = 0
            self.folder_create_flg = True
            self.crawl_url(url)
            #写入已访问过的列表文件
            self.write_visited_list(url)
        
    def get_urls(self,key_page, key_contents):
        ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        print(ymdhms + " 正在解析网页获取链接列表。。。")
        
        merge_urls=[]
        #循环条件：待抓取的链接不空
        while not len(unVisited)==0:
            #队头url出队列
            try:
                visitUrl = unVisited.pop()
            except:
                visitUrl = None
            if visitUrl is None or visitUrl=="":
                continue
            #print("Pop out one url from unvisited url list:" + visitUrl)
            #获取超链接
            pages=self.getPagesHyperLinks(visitUrl,key_page)
            links=self.getPagesHyperLinks(visitUrl,key_contents)
            merge_urls.extend(links)
            #将url放入已访问的url中
            visted.append(visitUrl)
            #print("Visited deepth: "+str(self.current_deepth))
            #未访问的url入列
            for page in pages:
                if page not in visted:
                    if page!="" and page not in visted and page not in unVisited:
                        unVisited.insert(0,page)
        #去除列表中重复元素
        target_urls = list(set(merge_urls))
        target_urls.sort(key=merge_urls.index)
        return target_urls
     
    def crawl_url(self, url):
        merge_urls = []
        if url!="" and url not in visted and url not in unVisited:
            unVisited.insert(0,url)
        #循环条件：待抓取的链接不空
        while not len(unVisited)==0:
            #队头url出队列
            try:
                visitUrl = unVisited.pop()
            except:
                visitUrl = None
            if visitUrl is None or visitUrl=="":
                continue
            #print("Pop out one url from unvisited url list:" + visitUrl)
            #获取超链接
            pages=self.getPagesHyperLinks(visitUrl,"pages")
            #将url放入已访问的url中
            visted.append(visitUrl)
            merge_urls.append(visitUrl)
            #print("Visited deepth: "+str(self.current_deepth))
            #未访问的url入列
            for page in pages:
                if page not in visted:
                    if page!="" and page not in visted and page not in unVisited:
                        unVisited.insert(0,page)
                    merge_urls.append(page)
        #去除列表中重复元素
        target_urls = list(set(merge_urls))
        target_urls.sort(key=merge_urls.index)

        for target_url in target_urls:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + " 正在获取: " + target_url)
            self.get_target(target_url)

    def get_target(self,url):
        page = self.get_PageHtml(url)
        #将url放入已访问的url中
        visted.append(url)
        if page is None:
            return None
        
        if self.folder_create_flg == True:
            title = self.get_html_title(page)
            self.path = savedir + "\\" + self.normalize_dir(title)
            self.mkDir(self.path)
            self.folder_create_flg = False
            
        target_list=page.xpath('//div[@id="big-pic"]//img/@src')

        for target in target_list:
            self.n+=1
            try:
                request.urlretrieve(target, self.path + '/%s.jpg' % self.n)
            except:
                ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print(ymdhms + "错误:下载失败" + target)
                self.log_writer(ymdhms + " 错误:下载失败 " + target)
        
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
                self.log_writer(ymdhms + " 错误:可能不是一个有效的href属性 " + href)
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
            print(ymdhms + " 链接打开失败: " + url)
            self.log_writer(ymdhms + " 链接打开失败: " + url)
            return None
        try:
            html = res.read()
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + " 链接读取错误: " + url)
            self.log_writer(ymdhms + " 链接读取错误: " + url)
            return None
        try:
            page = etree.HTML(self.utf8_transfer(html).lower())
            #html = utf8_transfer(html)
        except:
            ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            print(ymdhms + " 网页编码转换错误: " + url)
            self.log_writer(ymdhms + " 网页编码转换错误: " + url)
            return None
        return page
    
    #utf8编码转换
    def utf8_transfer(self,html):
        try:
            #charset = chardet.detect(html)['encoding']
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
            print(ymdhms + r"url拼接错误:",url)
            self.log_writer(ymdhms + r" url拼接错误: " + url)
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

    #加载已读取过的url列表
    def load_visited_list(self,path):
        f = open(path, "r")
        try:
            for line in f:
                line=line.strip('\n')
                visted.append(line)
        except Exception as e:
            print(e)
        finally:
            f.close()
        
    #记入已读取过的url列表
    def write_visited_list(self,url):
        f = open(".\\visitedList.txt","a")
        try:
            f.write(url + '\n')
        except Exception as e:
            print(e)
        finally:
            f.close()
            
    #日志记录
    def log_writer(self,msg):
        f = open(".\\crawl_log.log","a")
        try:
            f.write(msg + '\n')
        except Exception as e:
            print(e)
        finally:
            f.close()

#创建保存目录
def create_savedir():
    global savedir
    ymd = time.strftime("%Y%m%d", time.localtime())
    savedir = ".\\" + ymd

def main(seeds):
    create_savedir()
    craw=MyCrawler()
    craw.init1(seeds)
    craw.load_visited_list(".\\visitedList.txt")
    #craw.crawling()
    urls = craw.get_urls("pagenum","mainbody")
    try:
        executor = ThreadPoolExecutor(5)
        for url in urls:
            craw=MyCrawler()
            executor.submit(craw.crawling,(url))
    except:
        pass
    finally:
        executor.shutdown()

if __name__=="__main__":
    main("https://www.aitaotu.com/tag/chizuzhe.html")
    print("TASK OVER!!!")

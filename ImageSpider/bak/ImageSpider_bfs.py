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

visited_img = set()
folderDict = {}
web_title = ""
savedir = ""
keyword = ""

class MyCrawler:
    def __init__(self,seeds):
        #初始化当前抓取的深度
        self.current_deepth = 1
        #使用种子初始化url队列
        self.linkQuence=linkQuence()
        if isinstance(seeds,str):
            self.linkQuence.addUnvisitedUrl(seeds)
        if isinstance(seeds,list):
            for seed in seeds:
                self.linkQuence.addUnvisitedUrl([1.0, seed])
        print ("Add the seeds to the unvisited url list:" + str(self.linkQuence.unVisited))

    #抓取过程主函数
    def crawling(self,seeds,crawl_deepth):
        #循环条件：抓取深度不超过crawl_deepth
        while self.current_deepth <= crawl_deepth:
            #循环条件：待抓取的链接不空
            while not self.linkQuence.unVisitedUrlsEnmpy():
                #队头url出队列
                visitUrl=self.linkQuence.unVisitedUrlDeQuence()
                if visitUrl is None or visitUrl[1]=="":
                    continue
                print("Pop out one url from unvisited url list:" + visitUrl[1])
                #获取超链接
                links=self.getHyperLinks(visitUrl[1])
                #print("Get new links:" + str(len(links)))
                #将url放入已访问的url中
                self.linkQuence.addVisitedUrl(visitUrl)
                #print("Visited url count: "+str(self.linkQuence.getVisitedUrlCount()))
                print("Visited deepth: "+str(self.current_deepth))
            #未访问的url入列
            for link in links:
                self.linkQuence.addUnvisitedUrl(link)
            
            #url列表元素相似度降序排序
            url_list = sorted(self.linkQuence.getUnvisitedUrl(), key=lambda x:x[0], reverse=False)
            self.linkQuence.setUnvisitedUrl(url_list)
            #print("unvisited links:" + str(len(self.linkQuence.getUnvisitedUrl())))
            self.current_deepth += 1
    '''
    #获取源码中得超链接
    def getHyperLinks(self,url):
        links=[]
        data=self.getPageSource(url)
        if data[0]=="200":
            soup=BeautifulSoup(data[1])
            a=soup.findAll("a",{"href":re.compile('^http|^/')})
            for i in a:
                if i["href"].find("http://")!=-1:
                    links.append(i["href"]) 
        return links
    '''
    def getHyperLinks(self,url):
        url_list = []

        #去除url网页扩展名，对比用
        no_ext_url = self.get_no_ext_url(url)
        
        page = self.get_PageHtml(url)
        if page is None:
            return url_list
        
        #获取页面上的图片
        self.get_img(page,url)
        
        hrefs = page.xpath(u"//a")
        for href in hrefs:
            try:
                ret = href.get("href")
            except:
                ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                print(ymdhms + "错误:可能不是一个有效的href属性")
                continue
            #整理页面上的链接，相对url变换绝对url
            ret = self.join_sub_url(url, ret)

            if no_ext_url in ret:
                url_list.append((1.0, ret))
            else:
                #获取url相似度
                ratio = difflib.SequenceMatcher(lambda x: x in "_", url, ret).quick_ratio()
                #用相似度作为key把ret存入列表
                url_list.append((ratio, ret))

        return url_list

    #取得图片地址
    def get_img(self,page,url):
        global visited_img
        global web_title
        global keyword
        imgs = page.xpath(u"//img")
        if len(imgs) > 0:
            #取得页面tilte
            title = self.get_html_title(page)
            #页面title不包含输入的关键字，跳过
            keyword = r"丽柜"
            if (keyword is not None or keyword != "") and keyword not in title:
                return
            ratio = difflib.SequenceMatcher(lambda x: x in "_", title, web_title).quick_ratio()
            #页面标题相似度小于某值，创建新文件夹
            if ratio < 0.72:
                web_title = title
            else:
                title = web_title
            
            if title is None or title == "":
                title = r"未知标题"

            #创建文件夹
            global savedir
            path = savedir + "/" + self.normalize_dir(title)
            n = 1
            if self.mkDir(path):
                pass
            else:
                if title in folderDict:
                    n = folderDict[title]
                else:
                    #pass
                    return

            for img in imgs:
                img_url = img.get("src")
                #已下载过的图片链接忽视
                if img_url is None or img_url in visited_img:
                    continue
                try:
                    print(ymdhms + r"下载开始:",img_url)
                    local_dir = path + '/%s' + img_url[-4:]
                    request.urlretrieve(img_url, local_dir % n, self.callback)
                    #已下载过的图片链接记录
                    visited_img.add(img_url)
                    if self.filesize_filter(path + '/' + str(n) + img_url[-4:]):
                        n += 1
                        ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                        print(ymdhms + r"已下载:",img_url)
                except:
                    ymdhms = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
                    print(ymdhms + r"下载失败:",img_url)

            folderDict[title] = n
        
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
            print(ymdhms + r"url拼接错误:",img_url)
            return None

        return parse.urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

    #去除url扩展名
    def get_no_ext_url(self,url):
        if ".html" in url.lower() or \
           ".aspx" in url.lower():
            return url[:-5]
        elif ".htm" in url.lower() or \
             ".jsp" in url.lower() or \
             ".php" in url.lower() or \
             ".asp" in url.lower():
            return url[:-4]
        else:
            return url

    #获取网页源码
    '''
    def getPageSource(self,url,timeout=100,coding=None):
        try:
            socket.setdefaulttimeout(timeout)
            req = request.Request(url)
            req.add_header('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
            response = request.urlopen(req)
            page = ''
            if response.headers.get('Content-Encoding') == 'gzip':
                page = zlib.decompress(page, 16+zlib.MAX_WBITS)

            if coding is None:   
                coding= response.headers.getparam("charset")
            #如果获取的网站编码为None 
            if coding is None:
                page=response.read()
            #获取网站编码并转化为utf-8
            else:
                page=response.read()
                page=page.decode(coding).encode('utf-8')
            return ["200",page]
        except Exception as e:
            print(str(e))
            return [str(e),None]
    '''
    #获取网页源码
    def get_PageHtml(self,url,timeout=100,coding=None):
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

    #用re抽取网页Title
    def get_html_title(self,page):
        titles = page.xpath(u"//title")
        if titles is None or len(titles) == 0:
            title = ''
        else:
            title = titles[0].text
        return title

    #创建文件夹
    def mkDir(self,path):
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            #print(path + 'is already Exists')
            return False

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
    
    #文件大小过滤器
    def filesize_filter(self,filePath):
        #获取文件大小(KB)
        filesize = os.path.getsize(filePath)/1024
        #删除小于90KB的文件
        if filesize < 90:
            os.remove(filePath)
            return False
        return True
    
    #文件下载进度表示
    def callback(self,a,b,c):
        '''''回调函数
        @a:已经下载的数据块
        @b:数据块的大小
        @c:远程文件的大小
        '''
        per = 100.0*a*b/c
        if per > 100:
            per = 100
        print('%.2f%%' % per)

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
    main(["https://www.aitaotu.com/guonei/33222.html"],10)
    print("TASK OVER!!!")

#!/usr/bin/env Python
# coding=utf-8

import os
import time
import re
import chardet
import difflib
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
from posixpath import normpath

deep = 0
tmp = ""
visited_url = set()
visited_img = set()
folderDict = {}
url = ""
domain = ""
web_title = ""
savedir = ""
permit_url = ""

#网址校验
def check_url():
    global url
    global domain
    while True:
        url = input(r"请输入网址(http://...形式):")
        reg = r'^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$'
        pattern = re.compile(reg)
        regret = re.match(pattern, url, flags=0)
        if regret is None:
            print("网址无效，请重新输入")
            continue
        domain = parse.urlparse(url)[1]
        return

#爬取范围校验
def check_domain():
    global permit_url
    while True:
        permit_url = input(r"设定爬取范围(不设定可直接回车):")
        if permit_url is None or permit_url == "":
            return
        reg = r'^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$'
        pattern = re.compile(reg)
        regret = re.match(pattern, permit_url, flags=0)
        if regret is None:
            print("爬取范围无效，请重新输入")
            continue
        return

'''TODO
#目录校验
def check_dir():
    global savedir
    while True:
        savedir = input(r"请输入保存目录:")
        isExists = os.path.exists(savedir)
        if not isExists:
            print("目录无效，请重新输入")
            continue
        return
'''
#创建保存目录
def create_savedir():
    global savedir
    ymd = time.strftime("%Y%m%d", time.localtime())
#    savedir = savedir + "/" + ymd
#    isExists = os.path.exists(savedir)
#    if not isExists:
#        os.makedirs(savedir)
    savedir = ".\\" + ymd

#★★★前处理★★★
def pre_process():
    check_url()
    #check_dir()
    check_domain()
    create_savedir()

def get_local_pages(url,domain):
    global deep
    global visited_url
    global tmp
    repeat_time = 0
    pages = []
    
    #防止url读取卡住
    while True:
        try:
            time.sleep(1)
            #print("Opening the web", url)
            web = request.urlopen(url)
            #print("Success to Open the web")
            break
        except:
            #print("Open Url Failed !!! Repeat")
            time.sleep(1)
            repeat_time = repeat_time+1
            if repeat_time == 5:
                 return

    soup = BeautifulSoup(web.read(), "html.parser")
    tags = soup.findAll(name='a')
    url_list = []
    #去除url网页扩展名，对比用
    no_ext_url = get_no_ext_url(url)
    for tag in tags:
        #避免参数传递异常
        try:
            ret = tag['href']
        except:
            #print("Maybe not the attr : href")
            continue

        #整理页面上的链接，相对url变换绝对url
        ret = join_sub_url(url, ret)

        #url变换异常或已经访问过
        if ret is None or ret in visited_url:
            continue

        if no_ext_url in ret:
            url_list.append((1.0, ret))
        else:
            #获取url相似度
            ratio = difflib.SequenceMatcher(lambda x: x in "_", url, ret).quick_ratio()
            #用相似度作为key把ret存入列表
            url_list.append((ratio, ret))
        
    #url列表元素相似度降序排序
    url_list = sorted(url_list, key=lambda x:x[0], reverse=True)
    for ret in url_list:
        o = parse.urlparse(ret[1])
        #协议处理
        if 'http' not in o[0] and 'https' not in o[0]:
            #print("Bad  Page：" + ret.encode('ascii'))
            continue

        #url合理性校验
        if o[0] is "" and o[1] is not "":
            #print("Bad  Page: " + ret[1])
            continue

        #域名校验
        if domain not in o[1]:
            #print("Bad  Page: " + ret[1])
            continue

        #范围校验
        if permit_url not in ret[1]:
            continue

        #整理，输出
        newpage = ret[1]
        if newpage not in visited_url:
            #print("Add New Page: " + newpage)
            pages.append(newpage)
    return pages

#组装子网页url
def join_sub_url(base,url):
    try:
        url = parse.urljoin(base, url)
        arr = parse.urlparse(url)
        path = normpath(arr[2])
    except:
        return None

    return parse.urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))
            
#取得网页代码
def get_html(url):
    try:
        page = request.urlopen(url)
        html = page.read()
        html = utf8_transfer(html)
    except:
        print("链接打开失败:" + url)
        return ""
    return html

#取得图片地址
def get_img(html,url):
    global visited_img
    global web_title
    reg = r'http[s]?://\S+\.jpg'
    img_re = re.compile(reg)
    img_list = re.findall(img_re, html.lower())
    #print("★★★Count of Pictures★★★:", end="");print(len(img_list))
    if len(img_list) > 0:
        title = get_html_title(html)
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
        path = savedir + "/" + title
        n = 1
        if mkDir(path):
            pass
        else:
            if title in folderDict:
                n = folderDict[title]

        for img_url in img_list:
            #已下载过的图片链接忽视
            if img_url in visited_img:
                continue
            try:
                request.urlretrieve(img_url, path + '/%s.jpg' % n)
                if filesize_filter(path + '/' + str(n) + '.jpg'):
                    n += 1
                    #已下载过的图片链接记录
                    visited_img.add(img_url)
                    print(r"已下载:",img_url)
            except:
                pass
        folderDict[title] = n

#utf8编码转换
def utf8_transfer(html):
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
        #print('utf8_transfer error')
        pass
    return html

#用re抽取网页Title
def get_html_title(Html):
    compile_rule = r'<title>.*</title>'
    title_list = re.findall(compile_rule, Html)
    if title_list is None:
        title = ''
    else:
        title = title_list[0][7:-8]
    return title

#创建文件夹
def mkDir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        #print(path + 'is already Exists')
        return False
    
#文件大小过滤器
def filesize_filter(filePath):
    #获取文件大小(KB)
    filesize = os.path.getsize(filePath)/1024
    #删除小于90KB的文件
    if filesize < 90:
        os.remove(filePath)
        return False
    return True

#去除url扩展名
def get_no_ext_url(url):
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

#dfs算法遍历全站
def dfs(pages):
    #无法获取新的url说明遍历完成，即可结束dfs
    if pages==None or len(pages) == 0:
        #print("★★★pages==None:return")
        return
    global url
    global domain
    global visited_url
    
    for page in pages:
        if page not in visited_url:
            #print("Visiting",page)
            print("正在爬取链接:",page)
            visited_url.add(page)
            url = page
            pages = get_local_pages(url, domain)
            html = get_html(url)
            if html == "":
                continue
            get_img(html,url)
            dfs(pages)

    #print("sucess")

pre_process()
visited_url.add(url)
pages = get_local_pages(url, domain)
html = get_html(url)
get_img(html,url)
#递归开始
dfs(pages)


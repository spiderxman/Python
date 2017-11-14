#!/usr/bin/env Python
# coding=utf-8

import urllib
import urllib.request
from bs4 import BeautifulSoup
import time
import re
import os
import chardet

deep = 0
tmp = ""
sites = set()
visited = set()
folderDict = {}
#local = set()

def getandcheckInput():
    while True:
        inUrl = input(r"请输入网址:")
        reg = r'^((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?$'
        pattern = re.compile(reg)
        regret = re.match(pattern, inUrl, flags=0)
        if regret is not None:
            return inUrl

url = getandcheckInput()
purl = urllib.parse.urlparse(url)
domain = purl[1]
print("domain", domain)
def get_local_pages(url,domain):
    global deep
    global sites
    global tmp
    repeat_time = 0
    pages = set()

    #TODO
    #url = getandcheckInput()
    
    #防止url读取卡住
    while True:
        try:
            time.sleep(1)
            print("Opening the web", url)
            web = urllib.request.urlopen(url)
            print("Success to Open the web")
            break
        except:
            print("Open Url Failed !!! Repeat")
            time.sleep(1)
            repeat_time = repeat_time+1
            if repeat_time == 5:
                 return

    soup = BeautifulSoup(web.read(), "html.parser")
    tags = soup.findAll(name='a')
    for tag in tags:
        #避免参数传递异常
        try:
            ret = tag['href']
        except:
            print("Maybe not the attr : href")
            continue
        #o = urllib.parse.urlparse(ret)
        
        ret = get_url(ret)
        
        o = urllib.parse.urlparse(ret)
        #协议处理
        if 'http' not in o[0] and 'https' not in o[0]:
            #print("Bad  Page：" + ret.encode('ascii'))
            continue

        #url合理性检验
        if o[0] is "" and o[1] is not "":
            print("Bad  Page: " +ret)
            continue

        #域名检验
        if domain not in o[1]:
            print("Bad  Page: " +ret)
            continue

        #整理，输出
        newpage = ret
        if newpage not in sites:
            #print("Add New Page: " + newpage)
            pages.add(newpage)
    return pages

#取得子网页url
def get_url(ret):
    if "http://" in ret or "https://" in ret:
        pass
    elif "../" in ret:
        paths = ret.split('/')
        last_path = ""
        dotCount = 0
        for i in range(len(paths)):
            if paths[i] == '..':
                dotCount = dotCount + 1
                continue
            last_path = last_path + '/' + paths[i]
        obj = urllib.parse.urlparse(url)
        paths = obj[2].split('/')
        tmp_path = ''
        for i in range(len(paths)-dotCount-1):
            if paths[i] == '':
                continue
            tmp_path = tmp_path + '/' + paths[i]

        ret = obj[0] + "://" + obj[1] + tmp_path + last_path
    elif len(ret) > 0 and ret[0] == '/':
        obj = urllib.parse.urlparse(url)
        ret = obj[0] + "://" + obj[1] + ret
    else:
        obj = urllib.parse.urlparse(url)
        paths = obj[2].split('/')
        tmp_path = ''
        for i in range(len(paths)-1):
            if paths[i] == '':
                continue
            tmp_path = tmp_path + '/' + paths[i]
        tmp_path = tmp_path + '/' + ret

        ret = obj[0] + "://" + obj[1] + tmp_path
    return ret
            
#取得网页代码
def get_html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    html = utf8_transfer(html)
    return html

#取得图片地址
def get_img(html,url):
    #reg = r'src="(http[^"]+?\.jpg)"'
    reg = r'http[s]?://\S+\.jpg'
    img_re = re.compile(reg)
    img_list = re.findall(img_re, html)
    print("★★★Count of Pictures:", end="");print(len(img_list))
    if len(img_list) > 0:
        #创建文件夹
        obj = urllib.parse.urlparse(url)
        title = get_html_title(html)
        if title is None or title == "":
            title = "unknowTitle"
        path = "C:/Tang/Develop/Python/spierPictures/pic/20170927/" + title
        if mkDir(path):
            n = 1
            for img_url in img_list:
                try:
                    urllib.request.urlretrieve(img_url, path + '/%s.jpg' % n)
                    filesizeFilter(path + '/' + str(n) + '.jpg')
                    n += 1
                except:
                    pass
            folderDict[title] = n
        else:
            n = folderDict[title]
            for img_url in img_list:
                try:
                    urllib.request.urlretrieve(img_url, path + '/%s.jpg' % n)
                    filesizeFilter(path + '/' + str(n) + '.jpg')
                    n += 1
                except:
                    pass
            folderDict[title] = n

#utf8编码转换
def utf8_transfer(html):
    try:
        charset = chardet.detect(html)['encoding']
        print(r"★★★★网页编码形式" + charset)
        if chardet.detect(html)['encoding'] == 'GB2312':
            html = html.decode("gb2312", 'ignore')
        elif chardet.detect(html)['encoding'] == 'utf-8':
            html = html.decode('utf-8', 'ignore')
        elif chardet.detect(html)['encoding'] == 'gbk':
            html = html.decode('gbk', 'ignore')
    except:
        print('utf8_transfer error')
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
        print(path + 'is already Exists')
        return False
    
#文件大小过滤器
def filesizeFilter(filePath):
    #获取文件大小(KB)
    filesize = os.path.getsize(filePath)/1024
    #删除小于50KB的文件
    if filesize < 90:
        os.remove(filePath)

#dfs算法遍历全站
def dfs(pages):
    #无法获取新的url说明遍历完成，即可结束dfs
    if pages==None or len(pages) == 0:
        print("★★★pages==None:return")
        return
    global url
    global domain
    global sites
    global visited
    sites = set.union(sites,pages)
    for page in pages:
        if page not in visited:
            print("Visiting",page)
            visited.add(page)
            url = page
            pages1 = get_local_pages(url, domain)
            html = get_html(url)
            #for i in get_img(html,url):
            #    print(i)
            get_img(html,url)
            dfs(pages1)

    print("sucess")

pages = get_local_pages(url, domain)
dfs(pages)
#for i in sites:
#    print(i)

#!/usr/bin/env Python
# coding=utf-8

import urllib
import urllib.request
from bs4 import BeautifulSoup
import time
import re
 
url = "http://www.rentiyishu77.org/shineirenti/201709/13850.html"
domain = "rentiyishu77.org"
deep = 0
tmp = ""
sites = set()
visited = set()
n = 0
#local = set()
def get_local_pages(url,domain):
    global deep
    global sites
    global tmp
    repeat_time = 0
    pages = set()

    #防止url读取卡住
    while True:
        try:
            #print("Ready to Open the web!")
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

    #print("Readint the web ...")
    soup = BeautifulSoup(web.read(), "html.parser")
    #print("...")
    tags = soup.findAll(name='a')
    for tag in tags:

        #避免参数传递异常
        try:
            ret = tag['href']
        except:
            print("Maybe not the attr : href")
            continue
        o = urllib.parse.urlparse(ret)
        """
        #Debug I/O
        for _ret in o:
            if _ret == "":
                 pass
            else:
                 print _ret
        """

        if "http://" in ret or "https://" in ret:
            pass
        elif "../" in ret:
            paths = ret.split('/')
            for i in range(len(paths)):
                if paths[i] == '..':
                    paths[i] = ''
                    if paths[i-1]:
                        paths[i-1] = ''
            tmp_path = ''
            for path in paths:
                if path == '':
                    continue
                tmp_path = tmp_path + '/' +path
            ret =ret.replace(o[2],tmp_path)
        elif '/' not in ret:
            obj = urllib.parse.urlparse(url)
            paths = obj[2].split('/')
            tmp_path = ''
            for i in range(len(paths)-1):
                if paths[i] == '':
                    continue
                tmp_path = tmp_path + '/' + paths[i]
            tmp_path = tmp_path + '/' + ret

            ret = "http://"+obj[1]+tmp_path

        o = urllib.parse.urlparse(ret)
        #协议处理
        if 'http' not in o[0]:
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
            print("Add New Page: " + newpage)
            pages.add(newpage)
    return pages

#取得网页代码
def get_html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

#取得图片地址
def get_img(html):
    #reg = r'src="(http[^"]+?\.jpg)"'
    reg = r'http://\S+\.jpg'
    img_re = re.compile(reg)
    html=html.decode('gbk')#python3
    img_list = re.findall(img_re, html)
    global n
    print("★★★Count of Pictures:")
    print(len(img_list))
    for img_url in img_list:
        urllib.request.urlretrieve(img_url, 'C:/Tang/Develop/Python/spierPictures/pic/%s.jpg' % n)
        n += 1
    return img_list

#dfs算法遍历全站
def dfs(pages):
    print("★★★dfs Execute")
    print(len(pages))
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
            ht = get_html(url)
            for i in get_img(ht):
                print(i)
            dfs(pages1)

    print("sucess")

pages = get_local_pages(url, domain)
dfs(pages)
for i in sites:
    print(i)

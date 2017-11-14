#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib
import urllib.request
from bs4 import BeautifulSoup
import time
import re
 
url = "http://tieba.baidu.com/p/5004440579"
domain = "tieba.baidu.com"
deep = 0
tmp = ""
sites = set()
visited = set()
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
           print("Ready to Open the web!")
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

   print("Readint the web ...")
   soup = BeautifulSoup(web.read(), "html.parser")
   print("...")
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
       #处理相对路径url
       if o[0] is "" and o[1] is "":
           print("Fix  Page: " +ret)
           url_obj = urllib.parse.urlparse(web.geturl())
           #add by Tang St 20170923
           reg = r'^((?!\/).)*$'
           img_re = re.compile(reg)
           result = img_re.match(ret)
           if result!=None:
              paths = o[2].split('/')
              last = ""
              for i in range(len(paths)-1):
                 last = last + "/" + paths[i]

              ret = url_obj[0] + "://" + url_obj[1] + last

              #print("★★★★result!=None :")
              #print("url_obj[0] :"+ url_obj[0])
              #print("url_obj[1] :"+ url_obj[1])
              #print("url_obj[2] :"+ url_obj[2])
           else:
              ret = url_obj[0] + "://" + url_obj[1] + url_obj[2] + ret
              #print("★★★★result==None: ")
              #print("url_obj[0] :"+ url_obj[0])
              #print("url_obj[1] :"+ url_obj[1])
              #print("url_obj[2] :"+ url_obj[2])
           #add by Tang Ed 20170923
           #ret = url_obj[0] + "://" + url_obj[1] + url_obj[2] + ret
           #保持url的干净
           ret = ret[:8] + ret[8:].replace('//','/')
           o = urllib.parse.urlparse(ret)
           #这里不是太完善，但是可以应付一般情况
           if '../' in o[2]:
               paths = o[2].split('/')
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
           print("FixedPage: " + ret)

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
    #print("★★★url")
    #print(url)
    #print("★★★html")
    #print(html)
    return html

#取得图片地址
def get_img(html):
    #reg = r'src="(http[^"]+?\.jpg)"'
    reg = r'http://\S+\.jpg'
    img_re = re.compile(reg)
    html=html.decode('gb2312')#python3
    img_list = re.findall(img_re, html)
    n = 0
    print("★★★")
    print(len(img_list))
    for img_url in img_list:
        urllib.request.urlretrieve(img_url, 'C:/Tang/Develop/Python/spierPictures/pic/%s.jpg' % n)
        n += 1
    return img_list

#dfs算法遍历全站
def dfs(pages):
    #无法获取新的url说明便利完成，即可结束dfs
    if pages==None:
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
            pages = get_local_pages(url, domain)
            dfs(pages)
            ht = get_html(url)
            for i in get_img(ht):
                print(i)

    print("sucess")

pages = get_local_pages(url, domain)
dfs(pages)
for i in sites:
    print(i)

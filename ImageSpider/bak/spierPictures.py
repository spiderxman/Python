#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib.request
import re

def get_html(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

def get_img(html):
    #reg = r'src="(http[^"]+?\.jpg)"'
    reg = r'http://\S+\.jpg'
    img_re = re.compile(reg)
    html=html.decode('gb2312')#python3
    img_list = re.findall(img_re, html)
    n = 0
    for img_url in img_list:
        urllib.request.urlretrieve(img_url, 'C:/Tang/Develop/Python/spierPictures/pic/%s.jpg' % n)
        n += 1
    return img_list
    
ht = get_html("http://www.rentiyishu77.org/rentipengpai/201709/13857.html")
for i in get_img(ht):
    print(i)

#!/usr/bin/env Python
# coding=utf-8

import urllib
import urllib.request
import time
import re
from posixpath import normpath
'''
def join_sub_url(base,url):
    try:
        url = urllib.parse.urljoin(base, url)
        arr = urllib.parse.urlparse(url)
        path = normpath(arr[2])
    except:
        return ""
    return urllib.parse.urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))

suburl = join_sub_url("https://www.aitaotu.com/guonei/26360.html","/guonei/26360_2.html")
print(suburl)
suburl = join_sub_url("https://www.rentiyishu77.org/shineirenti/201709/13895.html","../201709/13892.html")
print(suburl)
'''
def normalize_dir():
    link = "https://www.aitaotu.com/guonei/26360.html"
    print(link.split('/'))
    #links = link.split('/')
    
    filename = link.split('/')[-1:][0]
    print(filename)
    print('26360.html')

normalize_dir()

#!/usr/bin/env Python
# coding=utf-8

import os
import time
import re
from urllib import request
from urllib import parse

#创建文件夹
def mkDir(path):
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        #print(path + 'is already Exists')
        return False

def get_imgs():
    #url = "https://img.aitaotu.cc:8089/Pics/2016/0415/09/01.jpg"
    year = 2017
    month = 1
    day = 20
    dir_no = 9
    img_no = 1
    no_data = 0

    while True:
        #time.sleep(1)
        url = "https://img.aitaotu.cc:8089/Pics/"
        url = url + str(year) + "/"
        url = url + str(month).zfill(2)
        url = url + str(day).zfill(2) + "/"
        url = url + str(dir_no).zfill(2) + "/"
        url = url + str(img_no).zfill(2)
        url = url + ".jpg"

        path = ".\\aitaotu\\"
        path = path + str(year) + str(month).zfill(2) + str(day).zfill(2) + str(dir_no).zfill(2)
        mkDir(path)

        try:
            path = path + '/%s' + url[-4:]
            request.urlretrieve(url, path % img_no)
            print(r"已下载:"+ url)
            no_data = 0
        except:
            print(r"下载失败:"+ url)
            no_data += 1

        #连续5次下载失败，基本可断定此目录已无可下载文件，进行下个目录的下载
        if no_data >= 5:
            img_no = 1
            dir_no += 1
            if dir_no >= 100:
                dir_no = 1
                day += 1
                if day >= 32:
                    day = 1
                    month += 1
                    if month >= 13:
                        month = 1
                        year += 1
            continue

        img_no += 1
        if img_no >= 100:
            img_no = 1
            dir_no += 1
            if dir_no >= 100:
                dir_no = 1
                day += 1
                if day >= 32:
                    day = 1
                    month += 1
                    if month >= 13:
                        month = 1
                        year += 1
get_imgs()

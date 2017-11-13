# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import re

class AitaotuPipeline(ImagesPipeline):
    
    def file_path(self, request, response=None, info=None):
        g_item = request.meta['g_item']
        title = g_item['title']
        folder_strip = strip(title)
        #image_guid = request.url.split('/')[-1]
        image_guid = strip(request.url)
        filename = u'full/{0}/{1}'.format(folder_strip, image_guid)
        return filename

    def get_media_requests(self, item, info):
        #for img_url in item['img_url']:
        img_url = item['img_url']
        title = item['title']
        yield Request(img_url, meta={'g_item': item}, dont_filter=False)
 
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item
    
#    def process_item(self, item, spider):
#        return item

def strip(path):
    """
    :param path: 需要清洗的文件夹名字
    :return: 清洗掉Windows系统非法文件夹名字的字符串
    """
    path = re.sub(r'[？\\*|“<>:]', '', str(path))
    path = re.sub(r'[/]', '$', str(path))
    return path
'''
if __name__ == "__main__":
    a = '我是一个？\*|“<>:/错误的字符串'
    print(strip(a))
'''
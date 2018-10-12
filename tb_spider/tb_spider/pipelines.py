# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

class TbSpiderPipeline(object):

    def process_item(self, item, spider):
        return item


class MiniMp4SpiderPipeline(object):
    # 初始化时打开文件
    def __init__(self, *args, **kwargs):
        self.f = open('minimp4movie.json','ab')

    def process_item(self, item, spider):
        # 去重
        # if item['id'] in self.ids_seen:
        #     raise DropItem("Duplicate item found: %s" % item)
        # else:
        #     self.ids_seen.add(item['id'])
        #     return item

        # 将scrapy items 转换成字典dict，在转换成json字符串
        data = json.dumps(dict(item), ensure_ascii=False) + ',\n'
        self.f.write(data.encode('utf-8'))
        return item

    # Override close_spider, 结束爬虫时关闭文件
    # 覆写方法，千万不要改名字
    def close_spider(self, spider):
        self.f.close()

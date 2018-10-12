# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TbSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MiniMp4Item(scrapy.Item):
	name = scrapy.Field()
	director = scrapy.Field()
	editors = scrapy.Field()
	actors = scrapy.Field()
	film_type = scrapy.Field()
	region = scrapy.Field()
	language = scrapy.Field()
	release_time = scrapy.Field()
	duaration = scrapy.Field()
	alias = scrapy.Field()
	douban_point = scrapy.Field()
	imdb_point = scrapy.Field()
	description = scrapy.Field()
	resources = scrapy.Field()
	comments = scrapy.Field()

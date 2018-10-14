# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import json
import pymysql


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

	def get_insert_sql(self):
		insert_sql =  '''insert into minimp4(
		id, 
		name, 
		region, 
		language, 
		release_time, 
		duaration, 
		douban_point, 
		imdb_point, 
		details
		) values (
			uuid(), %s, %s, %s, %s, %s, %s, %s, %s
		);'''	
		params = (
			pymysql.escape_string(self['name'][0] if len(self['name'])>0 else ''),
			pymysql.escape_string(self['region'][0] if len(self['region'])>0 else ''),
			pymysql.escape_string(self['language'][0] if len(self['language'])>0 else ''),
			pymysql.escape_string(self['release_time'][0] if len(self['release_time'])>0 else ''),
			pymysql.escape_string(self['duaration'][0] if len(self['duaration'])>0 else ''),
			pymysql.escape_string(self['douban_point'][0] if len(self['douban_point'])>0 else ''),
			pymysql.escape_string(self['imdb_point'][0] if len(self['imdb_point'])>0 else ''),
			pymysql.escape_string(json.dumps(dict(self), ensure_ascii=False))
		)
		return (insert_sql,params) 

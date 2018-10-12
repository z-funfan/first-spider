# -*- coding: utf-8 -*-
import scrapy
from tb_spider import items

class Minimp4Spider(scrapy.Spider):
    # Spider 唯一名称
    name = 'minimp4'
    # 域名限制
    allowed_domains = ['www.minimp4.com']
    # 爬取页面 从第一页到2306页 (列表推导式)
    start_urls = ['http://www.minimp4.com/movie/?page={0}'.format(page_num) for page_num in range(2306)]

    def parse(self, response):
        # 找到详情页面URL, xpath()返回的是列表
        hrefs = response.xpath('//div[@class="meta"]/h1/a/@href').extract()
        for itemUrl in hrefs:
            # 点击进入详情页面, 生成器yield,
            # 进入页面后，调用回调函数，解析各个字段
            yield scrapy.Request(itemUrl, callback=self.parseContent)
    
    def parseContent(self, response):
        name = response.xpath('//div[@class="movie-meta"]/h1/text()').extract()
        director = response.xpath('//div[@class="movie-meta"]/p/span[text()="导演："]/following-sibling::*/text()').extract()
        editors = response.xpath('//div[@class="movie-meta"]/p/span[text()="编剧："]/following-sibling::*/text()').extract()
        actors = response.xpath('//div[@class="movie-meta"]/p/span[text()="主演："]/following-sibling::*/text()').extract()
        film_type = response.xpath('//div[@class="movie-meta"]/p/span[text()="类型："]/following-sibling::*/text()').extract()
        region = response.xpath('//div[@class="movie-meta"]/p/span[text()="制片地区："]/following-sibling::*/text()').extract()
        language = response.xpath('//div[@class="movie-meta"]/p/span[text()="语言："]/../text()').extract()
        release_time = response.xpath('//div[@class="movie-meta"]/p/span[text()="上映时间："]/../text()').extract()
        duaration = response.xpath('//div[@class="movie-meta"]/p/span[text()="片长："]/../text()').extract()
        alias = response.xpath('//div[@class="movie-meta"]/p/span[text()="又名："]/../text()').extract()
        douban_point = response.xpath('//div[@class="movie-meta"]/p/a[starts-with(text(),"豆瓣")]/text()').extract()
        imdb_point = response.xpath('//div[@class="movie-meta"]/p/a[starts-with(text(),"IMDB")]/text()').extract()
        description = response.xpath('//div[@class="movie-introduce"]/p/text()').extract()
        resources = response.xpath('//div[@id="normalDown"]//child::a/@href').extract()
        comments = response.xpath('//div[contains(@class, "comment")]//child::div[@class="reply-content"]/text()').extract()

        miniItem = items.MiniMp4Item()
        miniItem['name'] = name
        miniItem['director'] = director
        miniItem['editors'] = editors
        miniItem['actors'] = actors
        miniItem['film_type'] = film_type
        miniItem['region'] = region
        miniItem['language'] = language
        miniItem['release_time'] = release_time
        miniItem['duaration'] = duaration
        miniItem['alias'] = alias
        miniItem['douban_point'] = douban_point
        miniItem['imdb_point'] = imdb_point
        miniItem['description'] = description
        miniItem['resources'] = resources
        miniItem['comments'] = comments
        # 生成数据结构
        yield miniItem

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql
from twisted.enterprise import adbapi

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

class MiniMp4MysqlPipeline(object):
    insert_sql = '''insert into minimp4(
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
           uuid(),
            '{name}',
            '{region}',
            '{language}',
            '{release_time}',
            '{duaration}',
            '{douban_point}',
            '{imdb_point}',
            '{details}'
        );'''

    # 初始化时获取 setting.py 配置
    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    # 打开spider时，初始化熟虑库连接
    # 定义from_crawler方法后，scrapy将不会调用 __init__(self, *args, **kwargs)
    def open_spider(self, *args, **kwargs):
       # 连接数据库
       self.connect = pymysql.connect(
           host=self.settings.get('MYSQL_HOST'),#数据库地址
           port=self.settings.get('MYSQL_PORT'),# 数据库端口
           db=self.settings.get('MYSQL_DBNAME'), # 数据库名
           user = self.settings.get('MYSQL_USER'), # 数据库用户名
           passwd=self.settings.get('MYSQL_PASSWD'), # 数据库密码
           charset='utf8', # 编码方式
           use_unicode=True)
       # 通过cursor执行增删查改
       self.cursor = self.connect.cursor();
       self.connect.autocommit(True)

    def process_item(self, item, spider):
        try:
            sqltext = self.insert_sql.format(
                name=pymysql.escape_string(item['name'][0]),
                region=pymysql.escape_string(item['region'][0]),
                language=pymysql.escape_string(item['language'][0]),
                release_time=pymysql.escape_string(item['release_time'][0]),
                duaration=pymysql.escape_string(item['duaration'][0]),
                douban_point=pymysql.escape_string(item['douban_point'][0]),
                imdb_point=pymysql.escape_string(item['imdb_point'][0]),
                details=pymysql.escape_string(json.dumps(dict(item), ensure_ascii=False)))
            self.cursor.execute(sqltext)
        except pymysql.err.IntegrityError as e:
            print('ERROR - Insert data failed: [{0}]'.format(repr(e)))
        except:
             print('Unknown error')
        else:
            print('Insert data successfully!')
        return item

    # Override close_spider, 
    # 覆写方法，千万不要改名字
    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

class MiniMp4MysqlPoolPipeline(object):

    # 初始化时获取 setting.py 配置
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings.get('MYSQL_HOST'),#数据库地址
            port=settings.get('MYSQL_PORT'),# 数据库端口
            db=settings.get('MYSQL_DBNAME'), # 数据库名
            user=settings.get('MYSQL_USER'), # 数据库用户名
            passwd=settings.get('MYSQL_PASSWD'), # 数据库密码
            charset='utf8', # 编码方式
            cursorclass=pymysql.cursors.DictCursor, # 指定 curosr 类型
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('pymysql',**dbparams)
        return cls(dbpool) # 相当于dbpool付给了这个类，self中可以得到

    # 使用twisted将mysql插入变成异步执行
    def process_item(self, item, spider):
        # 指定操作方法和操作的数据
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 指定异常处理方法
        query.addErrback(self.handle_error, item, spider) 

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print (failure)
        print("ERROR - Following item cannot be inserted into db:")
        print(repr(item))

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql,params=self.get_insert_sql(item)
        cursor.execute(insert_sql,params)

    def get_insert_sql(self, item):
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
            pymysql.escape_string( item['name'][0] if len(item['name'])>0 else ''),
            pymysql.escape_string(item['region'][0] if len(item['region'])>0 else ''),
            pymysql.escape_string(item['language'][0] if len(item['language'])>0 else ''),
            pymysql.escape_string(item['release_time'][0] if len(item['release_time'])>0 else ''),
            pymysql.escape_string(item['duaration'][0] if len(item['duaration'])>0 else ''),
            pymysql.escape_string(item['douban_point'][0] if len(item['douban_point'])>0 else ''),
            pymysql.escape_string(item['imdb_point'][0] if len(item['imdb_point'])>0 else ''),
            pymysql.escape_string(json.dumps(dict(item), ensure_ascii=False))
        )
        return (insert_sql,params)

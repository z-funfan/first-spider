# first-spider
A spider project based on scrapy in learning propose (http://www.minimp4.com/movie)


## Python笔记 - Scrapy爬虫

https://docs.scrapy.org/en/latest/intro/install.html

## Scrapy安装

```shell
python3 -m pip install --upgrade Scrapy
```

在Windows上安装可能会出现以下问题：

```
    building 'twisted.test.raiser' extension
    error: Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": http://landinghub.visualstudio.com/visual-cpp-build-tools

    ----------------------------------------
Command "C:\Users\Funfan\AppData\Local\Programs\Python\Python37\python.exe -u -c "import setuptools, tokenize;__file__='C:\\Users\\Funfan\\AppData\\Local\\Temp\\pip-install-ilx4u1g0\\Twisted\\setup.py';f=getattr(tokenize, 'open', open)(__file__);code=f.read().replace('\r\n', '\n');f.close();exec(compile(code, __file__, 'exec'))" install --record C:\Users\Funfan\AppData\Local\Temp\pip-record-lipvezrx\install-record.txt --single-version-externally-managed --compile" failed with error code 1 in C:\Users\Funfan\AppData\Local\Temp\pip-install-ilx4u1g0\Twisted\
```

需要手动安装需要的库
https://www.lfd.uci.edu/~gohlke/pythonlibs/

库的命名规则是这样的：{_库名_}-{_库版本_}-cp{_Python版本_}-cp{_Python版本_}m-win{_系统环境_}.whl，

比如我的机器是Windows64位，安装的Python 3.7.0，就需要下载Twisted‑18.7.0‑cp37‑cp37m‑win_amd64.whl

下载的时候注意根据自己的Python版本和Windows环境下载对应的库

下载完成后手动安装


```shell
python3 -m pip install D:\Download\Twisted‑18.7.0‑cp37‑cp37m‑win_amd64.whl
python3 -m pip install D:\Download\pywin32-224-cp37-cp37m-win_amd64.whl

```

## 简单例子

最简单的爬虫例子需要以下几步
1. 创建一个Scrapy项目
2. 定义提取的Item
3. 编写爬取网站的 spider 并提取 Item
4. 编写 Item Pipeline 来存储提取到的Item(即数据)

### 创建项目

```shell
scrapy startproject tb_spider
```

目录下将会创建一个jd_spder项目，当然一个项目可以有好几个爬虫


```
tb_spider/
    scrapy.cfg            # 部署配置

    tb_spider/             # 项目的Python模块, 一般从这里import代码
        __init__.py

        items.py          # items定义文件

        middlewares.py    # 项目爬虫、调度器、下载器中间件，有一些内置的钩子

        pipelines.py      # 管道钩子，输入输出

        settings.py       # 主要的运行时配置

        spiders/          # 真正的爬虫代码
            __init__.py
```

本来想爬某宝某东的，但奈何人家做了很多反爬虫，还有很多动态加载，对初学者来说极其不友好，退而求其次，我们去爬个电影网站http://www.minimp4.com/movie


### 定义Item

Item 是保存爬取到的数据的容器，提供了额外保护机制来避免拼写错误导致的未定义字段错误，其使用方法和python字典类似。

通过`scrapy.Field()`定义字段

```python
# -*- coding: utf-8 -*-

import scrapy

class MiniMp4Item(scrapy.Item):
	name = scrapy.Field()
	director = scrapy.Field()
	editors = scrapy.Field()
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

```


### 编写Spider

根据模板创建爬虫
语法: `scrapy genspider [-t template] <name> <domain>`
可用模板
- basic， 默认
- crawl
- csvfeed
- xmlfeed

创建爬虫

```shell
cd tb_spider
scrapy genspider minimp4 www.minimp4.com
```

在spders目录下生成了minimp4.py，如下
```python
# -*- coding: utf-8 -*-
import scrapy


class Minimp4Spider(scrapy.Spider):
    name = 'minimp4'
    allowed_domains = ['www.minimp4.com']
    start_urls = ['http://www.minimp4.com/']

    def parse(self, response):
        pass

```

- `name`: 用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。
- `start_urls`: 包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。
- `parse()`： 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。

根据实际情况，抓取对象
```python
# -*- coding: utf-8 -*-
import scrapy
from tb_spider import items

class Minimp4Spider(scrapy.Spider):
    # Spider 唯一名称
    name = 'minimp4'
    # 域名限制
    allowed_domains = ['www.minimp4.com']
    # 爬取页面 从第一页到2306页 (列表推导式)
    start_urls = ['http://www.minimp4.com/movie/?page={0}'.format(page_num) for page_num in range(2)]

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

```

### 存储数据

先做最简单的文件存储，存成json文件

```python
# -*- coding: utf-8 -*-
import json

class MiniMp4SpiderPipeline(object):
    
    def __init__(self, *args, **kwargs):
        # 初始化id集合，用于去重
        self.ids_seen = set()
        # 初始化时打开文件
        self.f = open('minimp4movie.json','ab')
        return super().__init__(*args, **kwargs)

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
```
### settings文件设置（主要设置内容）

为了启用一个Item Pipeline组件，你必须将它的类添加到 `ITEM_PIPELINES` 配置

```python
# 设置请求头部，添加url
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  "User-Agent" : "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
}

# 设置item——pipelines
ITEM_PIPELINES = {
    'tencent.pipelines.MiniMp4SpiderPipeline': 300,
}
```
分配给每个类的整型值，确定了他们运行的顺序，item按数字从低到高的顺序，通过pipeline，通常将这些数字定义在0-1000范围内。


### 运行

```shell
scrapy list # 列出项目中所有的爬虫
scrapy crawl minimp4 # 使用名为quotes的爬虫进行爬取
```

## Pipeline Mysql

上面的爬虫，只把数据寄到文件当中，这次将试着将数据存到Mysql的数据库当中。其中，将会用到数据库链接和连接池

### 创建数据库

mysql -uroot -p

mysql> create database spider DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
mysql> GRANT ALL PRIVILEGES ON spider.* TO 'spider'@'%' IDENTIFIED BY 'Spider@2018';

CREATE TABLE `spider`.`minimp4` (
  `id` VARCHAR(45) NOT NULL COMMENT 'UUID',
  `name` VARCHAR(128) NOT NULL COMMENT '电影名称',
  `region` VARCHAR(45) NULL COMMENT '制片地区',
  `language` VARCHAR(45) NULL COMMENT '语言',
  `release_time` VARCHAR(45) NULL COMMENT '上映时间',
  `duaration` VARCHAR(45) NULL COMMENT '片长',
  `douban_point` VARCHAR(45) NULL COMMENT '豆瓣评分',
  `imdb_point` VARCHAR(45) NULL COMMENT 'IMDB评分',
  `details` TEXT NULL COMMENT '所有抓取内容JSON',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
COMMENT = 'Spider contents for minimp4';

### 依赖库

Python 3.5+ 
```shell
python3 -m pip install --upgrade pymysql
```
```python
import pymysql.cursors

```

Python 3.4-
```shell
python3 -m pip install --upgrade PyMySQL
```
```python
import MySQLdb
```

### 实现Pipeline

先在`stting.py`面设置数据库配置，等会可以直接调用

```python
MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'spider'
MYSQL_USER = 'spider'
MYSQL_PASSWD = 'Spider@2018'
MYSQL_PORT = 3306

```

简单写法

覆写`from_crawler(cls, crawler)` 以及 `__init__(self, settings)`方法获取数据库配置

在`open_spider`中打开数据库连接，`close_spider`中关闭连接

在`process_item`中拼写数据库执行语句，表中插入数据

pipelines.py

```python
import json
import pymysql

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

```

连接池写法 

相比直接插入db，需要多导入一个库 `from twisted.enterprise import adbapi`

`from_settings(cls, settings)` 从settings.py获取设置，初始化连接池，并将连接池托管给类

`__init__(self, dbpool)` 获取连接池

`process_item`覆写item处理方法， 使用twisted将mysql插入变成异步执行

`do_insert` 覆写sql执行方法

`handle_error` 覆写异常处理方法

`get_insert_sql`拼写插入语句，如果把该方法放到item配置里，pipeline就能变成通用pipeline



```python
import json
import pymysql
from twisted.enterprise import adbapi

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
        # 如果把该方法放到item配置里，pipeline就能变成通用pipeline
        # insert_sql,params=item.get_insert_sql() 
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

```


# 入门案例


SoDo 的调度器是基于Redis的，同时提供Kafka的流式爬虫，下面展示单机下的一个案例作为入门案例。该案例用Mongodb作为存储数据库.分布式看后续文章

### step0: mongodb启动

[下载安装](https://www.mongodb.com/download-center/community)完Mongodb ,在安装目录下执行如下


```python
./mongod  1>/dev/null  2>&1  &
```
更多关于mongodb,请访问[链接](https://docs.mongodb.com/manual/core/document/)

### step1: kafka启动

[下载安装](http://kafka.apache.org/quickstart)完kafka之后，在安装目录下执行如下：

`启动zookeeper`

```
bin/zookeeper-server-start.sh config/zookeeper.properties 1>/dev/null  2>&1  &
```

`启动Kafka`
```
bin/kafka-server-start.sh config/server.properties 1>/dev/null  2>&1  &
```

更多关于Kafka,请访问[链接](http://kafka.apache.org)

### step2:  redis启动

[下载安装]((https://redis.io/download))完redis,进行redis的启动

```
redis-server 1>/dev/null  2>&1  &
```

更多关于Redis ,请访问[链接](https://redis.io/)


### step3: 创建一个爬虫项目

`1、安装依赖`
```
pip install -U sodo
```

`2、创建爬虫项目`

创建一个`helloworld` 项目，该项目是拿[ycombinator news板块](https://news.ycombinator.com/news)作为爬取目标,创建流程如下：

```python
mkdir workspace && cd workspace
scrapy startproject helloworld
cd helloworld
scrapy genspider ycombinator ycombinator.com
```

过程如下：

```
➜  tmp scrapy startproject helloworld
➜  tmp cd helloworld
➜  helloworld scrapy genspider ycombinator ycombinator.com
➜  helloworld find .
.
./helloworld
./helloworld/spiders
./helloworld/spiders/__init__.py
./helloworld/spiders/ycombinator.py
./helloworld/__init__.py
./helloworld/middlewares.py
./helloworld/settings.py
./helloworld/items.py
./helloworld/pipelines.py
./scrapy.cfg
```

在`ycombinator.py`写爬取逻辑,如下：

```python
# -*- coding: utf-8 -*-
from sodo.spider.kafka import KafkaTopicSpider
from sodo.utils.string import bytes_to_json

from ..items import YItem


class CustomKafkaSpider(KafkaTopicSpider):
    name = "ycombinator"
    allowed_domains = ["ycombinator.com"]
    topic = "ycombinator"  # default: name = "ycombinator"
    batch_size = -1  # batch_size=-1 --> get max_poll_records of kafka, batch_size=n (n > 0) get n recode once time
    request_params = {
        "method": 'POST',
    }
    
    # 可选
    def message_pre_process(self, message):
        return bytes_to_json(message).get("message").get("p")

    def parse(self, response):
        item = YItem()
        item['target'] = response.css("tr.athing").extract_first("")
        item['title'] = response.css("a.storylink").extract_first("")
        item['url'] = response.url
        item['topic_message'] = response.meta.get("topic_message", "")
        yield item
```

在`items.py`增加`YItem`,如下：
```python
import scrapy


class YItem(scrapy.Item):
    target = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    topic_message = scrapy.Field()
```

在`pipelines.py`增加数据入库逻辑，如下：

```python
# -*- coding: utf-8 -*-

import pymongo


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', sodo)
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(dict(item))
        return item
```

在`settings.py`中增加如下：

```python
ITEM_PIPELINES = {
    'helloworld.pipelines.MongoPipeline': 300,
}


MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "sodo"

SOOD_KAFKA_SPIDER_GROUP_ID = "ryan"  # kafka group id (分布式情况下用到)
SOOD_KAFKA_SPIDER_MESSAGE_PREFIX = 'https://news.ycombinator.com/news?p='   # 可选

SCHEDULER = "sodo.scheduler.redis.Scheduler"
DUPEFILTER_CLASS = "sodo.filter.redis.RedisDupeFilter"

SOOD_CLIENT_PARAMS = {
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
    },
    "kafka_consumer": {
        "bootstrap_servers": ['127.0.0.1:9092'],
    }
}
```

之后启动爬虫

```
scrapy crawl ycombinator
```

启动之后项目一直等待kafka 消息，运行如下逻辑，发送给Kafka消息

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kafka import KafkaProducer
import time
from sodo.utils.string import json_to_bytes

KAFKA_HOST = '127.0.0.1'
KAFKA_PORT = 9092


producer = KafkaProducer(bootstrap_servers=['{kafka_host}:{kafka_port}'.format(
    kafka_host=KAFKA_HOST,
    kafka_port=KAFKA_PORT,
)])


for i in range(1, 5):
    resource = {
        'code': 10111,
        'message': {
            'times': 1,
            'p': i,
        }
    }
    producer.send(topic='ycombinator', value=json_to_bytes(resource))
time.sleep(1)
```
发送之后，开始爬取，爬取完毕之后，Mongodb中sodo下`ycombinator`集合得到的就是爬取的数据,恭喜你完成一个基本案例!

[完整代码](https://github.com/ycvbcvfu/SoDo/tree/master/examples/helloworld)
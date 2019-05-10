# SoDo Tutorial

Sodo is Redis-based  scheduler and Message queue Spider for Scrapy,  Provide more flexible and practical ways for Scrapy.
Let's go ,Write your first Scrapy project base on  SoDo.In this tutorial, we'll use[Mongodb](https://docs.mongodb.com/manual/core/document/),[Redis](https://redis.io/),[Kafka](http://kafka.apache.org).


### step0: run  mongodb 

[Download and install](https://www.mongodb.com/download-center/community) Mongodb, Then run 


```python
./mongod  1>/dev/null  2>&1  &
```
more info visit [link](https://docs.mongodb.com/manual/core/document/)

### step1: run kafka

[Download and install](http://kafka.apache.org/quickstart) Kafka,Then run：

`run zookeeper`

```
bin/zookeeper-server-start.sh config/zookeeper.properties 1>/dev/null  2>&1  &
```

`run Kafka`
```
bin/kafka-server-start.sh config/server.properties 1>/dev/null  2>&1  &
```

more info visit [link](http://kafka.apache.org)

### step2:  run redis

[Download and install]((https://redis.io/download)) Redis,Then run：

```
redis-server 1>/dev/null  2>&1  &
```

more info visit [link](https://redis.io/)


### step3: create Our first Spider


`1、install Sodo`
```
pip install -U sodo
```

`2、create a spider porject`



Create a `helloworld` project, which takes the [ycombinator news](https://news.ycombinator.com/news) as the crawl target.

```python
mkdir workspace && cd workspace
scrapy startproject helloworld
cd helloworld
scrapy genspider ycombinator ycombinator.com
```

that's all：

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

`ycombinator.py`：

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

    # optional
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

`items.py`：
```python
import scrapy


class YItem(scrapy.Item):
    target = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    topic_message = scrapy.Field()
```

`pipelines.py` ：

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
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'sodo')
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

`settings.py` ：

```python
ITEM_PIPELINES = {
    'helloworld.pipelines.MongoPipeline': 300,
}


MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE = "sodo"

SOOD_KAFKA_SPIDER_GROUP_ID = "ryan"  # kafka group id 
SOOD_KAFKA_SPIDER_MESSAGE_PREFIX = 'https://news.ycombinator.com/news?p='   # optional

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

start spider:

```
scrapy crawl ycombinator
```

then, send message to kafka `ycombinator` topic, here are the tool script

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
now,spider is `Running`,and `Mongodb`'s `ycombinator` collection at `sodo` db has some data you want .
Congratulation！

[Tutorial Code](https://github.com/ycvbcvfu/SoDo/tree/master/examples/helloworld)
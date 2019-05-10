# Settings

### 客户端参数

对于真实生产环境参数可能受实际生产环境影响，所以`SoDo`提供对各种客户端了`任意`的参数配置。

```python
SODO_CLIENT_PARAMS = {
    "redis": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        'socket_timeout': 30,
        'socket_connect_timeout': 30,
        'retry_on_timeout': True,
        'encoding': 'utf-8',
    },
    "kafka_consumer": {
        "bootstrap_servers": ["127.0.0.1:9200"],
        "max_poll_records": 30,
        "consumer_timeout_ms": 500,
    },
    "kafka_producer": {
        "bootstrap_servers": ["127.0.0.1:9200"],
    }

}
```

### 调度器

```python
# ---------------SCHEDULER---------------------
## 爬虫打开的时候，是否清理队列
SCHEDULER_CLEAR_QUEUE_AT_OPEN = False
## server pop 的timeout 参数
SCHEDULER_QUEUE_POP_TIMEOUT = 0
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_PRIORITY_QUEUE = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
## 过滤器类，
SCHEDULER_DUPEFILTER_CLASS = 'sodo.filter.redis.RedisDupeFilter'
## 序列化
SCHEDULER_QUEUE_SERIALIZER = 'sodo.utils.serialize.PickleSerializer'

## 是否要加kafka message 作为指纹
FINGERPRINT_BY_KAFKA_MESSAGE = True
## 默认设置为BloomFilter过滤器
SCHEDULER_FILTER_CLASS = 'sodo.filter.BloomFilter'
## BloomFilter的CAPACITY值
SCHEDULER_BLOOMFILTER_CAPACITY = 100000000
## BloomFilter的p值
SCHEDULER_BLOOMFILTER_ERROR_RATE = 0.00000001

## 是否日志
DUPEFILTER_LOG = True
## 是否debug
DUPEFILTER_DEBUG = False

# Kafka default settings
KAFKA_REDIS_KEY_FORMAT = 'kafka:%(module)s:%(topic)s:%(partition)s'
# Kafka 优先队列
SODO_KAFKA_PRIORITY_PARTITION = 1
```
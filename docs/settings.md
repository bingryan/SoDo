# Settings

### client params

Yes, Parameters of each client by yourself. Here is the default


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
    }

}
```

### scheduler

```python
# ---------------SCHEDULER---------------------
SCHEDULER_CLEAR_QUEUE_AT_OPEN = False
SCHEDULER_QUEUE_POP_TIMEOUT = 0
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_PRIORITY_QUEUE = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'sodo.filter.redis.RedisDupeFilter'
SCHEDULER_QUEUE_SERIALIZER = 'sodo.utils.serialize.PickleSerializer'

FINGERPRINT_BY_KAFKA_MESSAGE = True
SCHEDULER_FILTER_CLASS = 'sodo.filter.BloomFilter'
SCHEDULER_BLOOMFILTER_CAPACITY = 100000000
SCHEDULER_BLOOMFILTER_ERROR_RATE = 0.00000001

DUPEFILTER_LOG = True
DUPEFILTER_DEBUG = False

# Kafka default settings
KAFKA_REDIS_KEY_FORMAT = 'kafka:%(module)s:%(topic)s:%(partition)s'
SODO_KAFKA_PRIORITY_PARTITION = 1
```
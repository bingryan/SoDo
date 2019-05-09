#!/usr/bin/env python
# -*- coding: utf-8 -*-


HOOK_PROCESSOR = 'sodo.hook.HookSuperManager'

SODO_HOOKS_BASE = {
    "engine_started": {"sodo.hook.engine_started_default_hook_cls": 1},
    "engine_stopped": {"sodo.hook.engine_stopped_default_hook_cls": 1},
    "spider_opened": {"sodo.hook.spider_opened_default_hook_cls": 1},
    "spider_idle": {"sodo.hook.spider_idle_default_hook_cls": 1},
    "spider_closed": {"sodo.hook.spider_closed_default_hook_cls": 1},
    "spider_error": {"sodo.hook.spider_error_default_hook_cls": 1},
    "request_scheduled": {"sodo.hook.request_scheduled_default_hook_cls": 1},
    "request_dropped": {"sodo.hook.request_dropped_default_hook_cls": 1},
    "request_reached_downloader": {"sodo.hook.request_reached_downloader_default_hook_cls": 1},
    "response_received": {"sodo.hook.response_received_default_hook_cls": 1},
    "response_downloaded": {"sodo.hook.response_downloaded_default_hook_cls": 1},
    "item_scraped": {"sodo.hook.item_scraped_default_hook_cls": 1},
    "item_dropped": {"sodo.hook.item_dropped_default_hook_cls": 1},
    "item_error": {"sodo.hook.item_error_default_hook_cls": 1},
}

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
# ---------------SCHEDULER---------------------
SCHEDULER_CLEAR_QUEUE_AT_OPEN = False
SCHEDULER_QUEUE_POP_TIMEOUT = 0
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_PRIORITY_QUEUE = 'sodo.queue.RedisPriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'sodo.filter.redis.RedisDupeFilter'
SCHEDULER_QUEUE_SERIALIZER = 'sodo.utils.serialize.PickleSerializer'

FINGERPRINT_BY_KAFKA_MESSAGE = False
SCHEDULER_FILTER_CLASS = 'sodo.filter.BloomFilter'
SCHEDULER_BLOOMFILTER_CAPACITY = 100000000
SCHEDULER_BLOOMFILTER_ERROR_RATE = 0.00000001

DUPEFILTER_LOG = True
DUPEFILTER_DEBUG = False

# Kafka default settings
KAFKA_REDIS_KEY_FORMAT = 'kafka:%(module)s:%(topic)s:%(partition)s'
SODO_KAFKA_PRIORITY_PARTITION = 1

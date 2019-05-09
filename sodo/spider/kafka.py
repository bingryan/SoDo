#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from scrapy.http import Request
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider
from kafka import TopicPartition
from scrapy import signals
from sodo.utils.string import bytes_to_str
from sodo.utils.connection import kafka_consumer_from_settings, client_from_settings
from sodo import default_settings
from sodo.hook import HookABC

logger = logging.getLogger(__name__)


class KafkaMixin(HookABC):
    logger = logger

    """
    Mixin class to implement reading message from kafka topic.
    """
    topic = None
    group_id = None
    batch_size = None
    topic_partitions = None
    request_url_prefix = None
    request_params = {
        "method": 'GET'
    }
    kafka_priority_partition = 1
    count = 0

    def set_kafka(self, crawler=None):
        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if not hasattr(self, 'topic'):
            self.topic = self.name
        self.group_id = settings.get('SODO_KAFKA_SPIDER_GROUP_ID', self.group_id)
        self.request_url_prefix = settings.get('SODO_KAFKA_SPIDER_MESSAGE_PREFIX', self.request_url_prefix)
        self.request_url_prefix = settings.get('SODO_KAFKA_SPIDER_URL_PREFIX', self.request_url_prefix)
        self.kafka_priority_partition = settings.getint("SODO_KAFKA_PRIORITY_PARTITION",
                                                        default_settings.SODO_KAFKA_PRIORITY_PARTITION)
        if self.batch_size is None:
            # set kafka batch size, CONCURRENT_REQUESTS for default.
            self.batch_size = settings.getint(
                'SODO_KAFKA_START_MESSAGE_BATCH_SIZE',
                settings.getint('CONCURRENT_REQUESTS'),
            )

        self.consumer = self.set_consumer(settings)
        self.logger.info("Start Pull Messages from kafka topic '%s'" % self.topic)

    def set_consumer(self, settings):
        raise NotImplementedError('{} set_consumer is not defined'.format(self.__class__.__name__))

    def message_pre_process(self, message):
        """pre process kafka message  before into KafkaTopicSpider"""
        return message

    def next_requests(self):
        """
        Pull data from  kafka  and get a request to be scheduled.
        """
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    def make_request_from_message(self, msg):
        """
        :param msg: message from kafka
        :return:
        """
        url = bytes_to_str(self.message_pre_process(msg))
        if self.request_url_prefix is not None:
            url = self.request_url_prefix + str(url)

        return self.make_requests_from_url(url, meta={'topic_message': bytes_to_str(msg)})

    def make_requests_from_url(self, url, meta=None):
        return Request(url, meta=meta, **self.request_params)

    def schedule_next_request(self):
        """Schedules a request  if available """
        requests = self.next_requests()
        if requests is not None:
            for req in requests:
                if req is not None:
                    self.crawler.engine.crawl(req, spider=self)

    # ----------------------------default signals hooks-----------------------------

    def spider_idle_hook(self, *args, **kwargs):
        """Default hook:Schedules a request if available, otherwise waits."""
        self.schedule_next_request()
        raise DontCloseSpider

    def item_scraped_hook(self, *args, **kwargs):
        self.schedule_next_request()

    def _set_crawler(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.set_kafka(crawler)
        self._set_signals(crawler)
        self._set_kafka_topic_spider_signals(crawler)

    def _set_kafka_topic_spider_signals(self, crawler):
        crawler.signals.connect(self.spider_idle_hook,
                                signal=signals.spider_idle)
        crawler.signals.connect(self.item_scraped_hook,
                                signal=signals.item_scraped)


class KafkaAutoCommitMixin(KafkaMixin):

    def next_requests(self):
        """
        Pull data from  kafka  and get a request to be scheduled.
        """
        if self.batch_size == -1:
            self.logger.info("Fetch ALL Messages from kafka topic： '%s'" % self.topic)
            for message in self.consumer:
                yield self.make_request_from_message(message.value)

        count = 0
        for message in self.consumer:
            req = self.make_request_from_message(message.value)
            if req:
                yield req
                count += 1
                if not count < self.batch_size:
                    break
            else:
                self.logger.info("Request not made from message: %r", message)
        if count:
            self.logger.info("Read %s requests from topic : '%s'", count, self.topic)

    def set_consumer(self, settings):
        return kafka_consumer_from_settings(settings, self.topic,
                                            group_id=self.group_id)


class KafkaNotAutoCommitMixin(KafkaMixin):
    """
    key: 'kafka:%(module)s:%(topic_name)s:%(partition)s'
    value: offset
    """

    def set_consumer(self, settings):
        kafka_consumer_client = kafka_consumer_from_settings(settings, group_id=self.group_id, enable_auto_commit=False)
        if self.topic_partitions is None:
            self.topic_partitions = kafka_consumer_client.partitions_for_topic(self.topic)
        return kafka_consumer_client

    def get_partition_offset(self, partition):
        """
        :param partition:
        :return:
        """
        key = self.kafka_redis_key_format % {"module": "spider", "topic": self.topic, "partition": partition}
        offset = self.redis_client.get(key)
        if offset is None:
            tp = TopicPartition(topic=self.topic, partition=partition)
            offset = self.consumer.end_offsets([tp])[tp]
            # update offset to redis
            self.update_partition_offset(partition=partition, offset=offset)
        return int(bytes_to_str(offset))

    def get_partitions(self):
        """get consumer kafka topic partitions"""
        return [partition for partition in self.topic_partitions]

    def update_partition_offset(self, partition: int, offset: int):
        """
        :param partition:  partition
        :param offset: offset
        :return:
        """
        key = self.kafka_redis_key_format % {"module": "spider", "topic": self.topic, "partition": partition}
        self.redis_client.set(key, offset)

    def set_redis_client(self, crawler=None):
        if crawler is None:
            crawler = getattr(self, 'crawler', None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings
        self.kafka_redis_key_format = settings.get("KAFKA_REDIS_KEY_FORMAT", default_settings.KAFKA_REDIS_KEY_FORMAT)
        self.redis_client = client_from_settings(settings)

    def start_consumer(self):
        if self.batch_size == -1:
            msg = self.consumer.poll(timeout_ms=200)
            self.logger.info(
                "Fetch ALL Messages from kafka topic： {} ".format(self.topic))
            if len(msg) > 0:
                for messages in msg.values():
                    for message in messages:
                        self.update_partition_offset(message.partition, message.offset)
                        yield self.make_request_from_message(message.value)
        if self.batch_size > 0:
            count = 0
            msg = self.consumer.poll(timeout_ms=200, max_records=self.batch_size)
            for messages in msg.values():
                if len(msg) > 0:
                    for message in messages:
                        req = self.make_request_from_message(message.value)
                        if req:
                            self.update_partition_offset(message.partition, message.offset)
                            yield req
                            count += 1
                            if not count < self.batch_size:
                                break
                        else:
                            self.logger.info("Request not made from message: %r", message)
            if count:
                self.logger.info("Read %s requests from topic : '%s'", count, self.topic)

    def next_requests(self):
        tps = [TopicPartition(topic=self.topic, partition=p) for p in self.topic_partitions]
        self.consumer.assign(tps)
        for partition in self.topic_partitions:
            offset = self.get_partition_offset(partition)
            self.consumer.seek(TopicPartition(topic=self.topic, partition=partition), offset)
        return self.start_consumer()


class KafkaTopicPriorityMixin(KafkaNotAutoCommitMixin):

    def fetch_one_message_by_partition(self, partition, max_records=1):
        current_offset = self.get_partition_offset(partition)
        topic_partition = TopicPartition(topic=self.topic, partition=partition)
        self.consumer.assign([topic_partition])
        self.consumer.seek(topic_partition, current_offset + 1)
        res = self.consumer.poll(timeout_ms=100, max_records=max_records)
        self.consumer.seek(topic_partition, current_offset)
        return res

    def set_consumer(self, settings):
        kafka_consumer_client = kafka_consumer_from_settings(settings, group_id=self.group_id, enable_auto_commit=False)
        if self.topic_partitions is None:
            self.topic_partitions = kafka_consumer_client.partitions_for_topic(self.topic)
        return kafka_consumer_client

    def next_requests(self):

        if self.kafka_priority_partition not in self.get_partitions():
            raise ValueError(" kafka num.partitions not greater than 1 or  partition num out of range")

        one_msg = self.fetch_one_message_by_partition(self.kafka_priority_partition)

        if len(one_msg) > 0:
            return self.start_consumer()
        else:
            other_partition = [partition for partition in self.get_partitions() if
                               partition != self.kafka_priority_partition]
            self.consumer.assign(
                [TopicPartition(topic=self.topic, partition=partition) for partition in other_partition])
            for partition in other_partition:
                partition_offset = self.get_partition_offset(partition)
                self.consumer.seek(TopicPartition(topic=self.topic, partition=partition), partition_offset + 1)
            return self.start_consumer()


class KafkaTopicPrioritySpider(KafkaTopicPriorityMixin, Spider):
    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(KafkaTopicPrioritySpider, self).from_crawler(crawler, *args, **kwargs)
        obj.set_redis_client(crawler)
        return obj

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))


class KafkaTopicPriorityCrawlSpider(KafkaTopicPriorityMixin, CrawlSpider):
    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(KafkaTopicPriorityCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.set_redis_client(crawler)
        return obj

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))


class KafkaTopicAdvancedSpider(KafkaNotAutoCommitMixin, Spider):

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(KafkaTopicAdvancedSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.set_redis_client(crawler)
        return obj

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))


class KafkaTopicAdvancedCrawlSpider(KafkaNotAutoCommitMixin, CrawlSpider):

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(KafkaTopicAdvancedCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.set_redis_client(crawler)
        return obj

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))


class KafkaTopicSpider(KafkaAutoCommitMixin, Spider):

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))


class KafkaTopicCrawlSpider(KafkaAutoCommitMixin, CrawlSpider):
    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

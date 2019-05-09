#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from scrapy.utils.serialize import ScrapyJSONEncoder
from kafka import KafkaProducer
from sodo.utils.string import str_to_bytes


class KafkaPipeline(object):
    """
    Publishes a serialized item into a Kafka topic

    :param producer: The Kafka producer
    :type producer: kafka.producer.Producer

    :param topic: The Kafka topic being used
    :type topic: str or unicode

    """

    def __init__(self, producer, topic):
        """
        :type producer: kafka.producer.Producer
        :type topic: str or unicode
        """
        self.producer = producer
        self.topic = topic

    def process_item(self, item, spider):
        resource = {
            'spider': spider.name,
            'data': {
                'item': dict(item)
            }
        }
        self.producer.send(self.topic, str_to_bytes(json.dumps(resource, cls=ScrapyJSONEncoder)))
        return item

    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings

        :rtype: A :class:`~KafkaPipeline` instance
        """
        topic = settings.get('ZEN_KAFKA_PIPELINE_TOPIC', 'zen_kafka_pipeline_topic')
        producer = KafkaProducer(bootstrap_servers=settings.get('ZEN_KAFKA_PIPELINE_HOST', ['localhost:9092']))
        return cls(producer, topic)

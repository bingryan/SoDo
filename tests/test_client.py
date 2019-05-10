#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sodo.utils.connection import client_from_settings, get_client, kafka_consumer_from_settings, \
    kafka_producer_from_settings
from sodo.default_settings import SODO_CLIENT_PARAMS

MOCK_SETTINGS = {
    "SODO_CLIENT_PARAMS": SODO_CLIENT_PARAMS
}


class TestGetClient(object):

    def test_get_redis_client(self):
        redis_server = client_from_settings(MOCK_SETTINGS)
        assert isinstance(redis_server, get_client("redis"))

    def test_get_kafka_consumer_client(self):
        kafka_consumer = kafka_consumer_from_settings(MOCK_SETTINGS)
        assert isinstance(kafka_consumer, get_client("kafka_consumer"))

    def test_get_kafka_producer_client(self):
        kafka_producer = kafka_producer_from_settings(MOCK_SETTINGS)
        assert isinstance(kafka_producer, get_client("kafka_producer"))

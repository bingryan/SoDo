#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sodo.default_settings import SODO_CLIENT_PARAMS
import redis
import kafka

"""
Returns a server(SSDB or redis) form settings
"""


def dict_merge(*dicts):
    merged = {}
    for d in dicts:
        if d is None:
            d = {}
        merged.update(d)
    return merged


def get_client(name="redis"):
    clients = {
        "redis": redis.Redis,
        "kafka_consumer": kafka.KafkaConsumer,
        "kafka_producer": kafka.KafkaProducer,
    }
    return clients[name]


def client_from_settings(settings, *args, **kwargs):
    client_name = None
    if kwargs.get("client_name") is not None:
        client_name = kwargs.pop("client_name")
    if client_name is None:
        client_name = "redis"
    client_config = dict_merge(SODO_CLIENT_PARAMS.get(client_name), settings['SODO_CLIENT_PARAMS'][client_name], kwargs)
    client_name = get_client(client_name)
    return client_name(*args, **client_config)


redis_client_from_settings = client_from_settings


def kafka_consumer_from_settings(settings, *args, **kwargs):
    return client_from_settings(settings, client_name="kafka_consumer", *args, **kwargs)


def kafka_producer_from_settings(settings, *args, **kwargs):
    return client_from_settings(settings, client_name="kafka_producer", *args, **kwargs)

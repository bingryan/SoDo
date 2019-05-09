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

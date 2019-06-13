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

        # TODO: 保留历史文件
        # 可以返回两个item
        # step1: 保留html

        yield item

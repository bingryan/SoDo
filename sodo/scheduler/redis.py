#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from scrapy.utils.misc import load_object, create_instance
from sodo import default_settings
from sodo.utils.connection import client_from_settings

logger = logging.getLogger(__name__)


class Scheduler(object):
    logger = logger

    def __init__(self, dupefilter, queue=None, stats=None, crawler=None,
                 scheduler_queue_pop_timeout=None, scheduler_clear_queue_at_open=None):
        self.df = dupefilter
        self.queue = queue
        self.scheduler_queue_pop_timeout = scheduler_queue_pop_timeout,
        self.scheduler_clear_queue_at_open = scheduler_clear_queue_at_open,
        self.stats = stats
        self.crawler = crawler
        self.spider = crawler.spider

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        # ------------------------dupefilter-------------------------
        dupefilter_cls = load_object(settings.get("DUPEFILTER_CLASS", default_settings.SCHEDULER_DUPEFILTER_CLASS))
        dupefilter = create_instance(dupefilter_cls, None, crawler)
        server = client_from_settings(settings)
        # ------------------------scheduler-------------------------
        scheduler_queue_class = load_object(default_settings.SCHEDULER_PRIORITY_QUEUE)
        scheduler_queue_key = settings.get("SCHEDULER_QUEUE_KEY",
                                           default_settings.SCHEDULER_QUEUE_KEY)
        scheduler_serializer = load_object(settings.get("SCHEDULER_QUEUE_SERIALIZER",
                                                        default_settings.SCHEDULER_QUEUE_SERIALIZER))
        # TODO: Make scheduler_queue_key more diverse
        queue = create_instance(scheduler_queue_class, None, crawler, server,
                                str(scheduler_queue_key % {'spider': crawler.spider.name}),
                                scheduler_serializer)
        scheduler_queue_pop_timeout = settings.get("SCHEDULER_QUEUE_POP_TIMEOUT",
                                                   default_settings.SCHEDULER_QUEUE_POP_TIMEOUT)
        scheduler_clear_queue_at_open = settings.get("SCHEDULER_CLEAR_QUEUE_AT_OPEN",
                                                     default_settings.SCHEDULER_CLEAR_QUEUE_AT_OPEN)
        return cls(dupefilter, queue=queue,
                   stats=crawler.stats,
                   crawler=crawler,
                   scheduler_queue_pop_timeout=scheduler_queue_pop_timeout,
                   scheduler_clear_queue_at_open=scheduler_clear_queue_at_open)

    def has_pending_requests(self):
        return len(self) > 0

    def open(self, spider):
        self.spider = spider
        if self.scheduler_clear_queue_at_open:
            # TODO: clear scheduler_queue_class and dupefilter_cls, not clear for default
            self.clear()
        return self.df.open()

    def clear(self):
        self.queue.clear()
        self.df.clear()
        self.logger.info("Clean up the dupefilter and scheduler queue successfully")

    def close(self, reason):
        return self.df.close(reason)

    def enqueue_request(self, request):
        if not request.dont_filter and self.df.request_seen(request):
            self.df.log(request, self.spider)
            return False
        if self.stats:
            self.stats.inc_value('scheduler/enqueued/redis', spider=self.spider)
        self.queue.push(request)
        return True

    def next_request(self):
        request = self.queue.pop(self.scheduler_queue_pop_timeout)
        if request and self.stats:
            self.stats.inc_value('scheduler/dequeued/redis', spider=self.spider)
        return request

    def __len__(self):
        return len(self.queue)

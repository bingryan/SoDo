#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.spiders import Spider as ScrapySpider
from scrapy.spiders import CrawlSpider as ScrapyCrawlSpider
from sodo.hook import HookABC
from scrapy import signals


class Spider(ScrapySpider, HookABC):

    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    def _set_crawler(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self._set_signals(crawler)
        crawler.signals.connect(self.close, signals.spider_closed)


class CrawlSpider(ScrapyCrawlSpider, HookABC):
    def parse(self, response):
        raise NotImplementedError('{}.parse callback is not defined'.format(self.__class__.__name__))

    def set_crawler(self, crawler):
        super(CrawlSpider, self).set_crawler(crawler)
        self._set_signals(crawler)
        self._follow_links = crawler.settings.getbool('CRAWLSPIDER_FOLLOW_LINKS', True)


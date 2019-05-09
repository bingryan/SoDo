#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import pprint

from scrapy import signals
from scrapy.utils.defer import process_chain
from collections import defaultdict
from scrapy.utils.misc import load_object, create_instance
from scrapy.utils.conf import build_component_list
from sodo.default_settings import SODO_HOOKS_BASE, HOOK_PROCESSOR
from scrapy.exceptions import NotConfigured
from scrapy.settings import Settings

logger = logging.getLogger(__name__)

HOOKS_LIST = ["engine_started", "engine_stopped", "spider_opened", "spider_idle", "spider_closed", "spider_error",
              "request_scheduled", "request_dropped", "request_reached_downloader", "response_received",
              "response_downloaded", "item_scraped", "item_dropped", "item_error"]


def _default_hook(hook_name):
    if hook_name is None:
        hook_name = "foo hook"
    hook_name = hook_name

    class DefaultHook(HooKBase):
        def process_hook(self, *args):
            logger.info("Start {} Spider at {} Hook".format(self.crawler.spider.name, hook_name))

    return DefaultHook


class HookManager(object):
    """ hook managers"""

    component_name = 'foo hook'

    def __init__(self, crawler, *hooks):
        self.crawler = crawler
        self.hooks = hooks
        self.methods = defaultdict(list)
        for hook in hooks:
            self._add_hook(hook)

    @classmethod
    def _get_hk_list_from_settings(cls, settings):
        return build_component_list(settings.getdict(cls.component_name))

    @classmethod
    def from_settings(cls, settings, crawler=None):

        hklist = cls._get_hk_list_from_settings(settings)
        hooks = []
        enabled = []
        for clspath in hklist:
            try:
                hkcls = load_object(clspath)
                hk = create_instance(hkcls, settings, crawler)
                hooks.append(hk)
                enabled.append(clspath)
            except NotConfigured as e:
                if e.args:
                    clsname = clspath.split('.')[-1]
                    logger.warning("Disabled %(clsname)s: %(eargs)s",
                                   {'clsname': clsname, 'eargs': e.args[0]},
                                   extra={'crawler': crawler})

        logger.info("Enabled %(componentname)ss:\n%(enabledlist)s",
                    {'componentname': cls.component_name,
                     'enabledlist': pprint.pformat(enabled)},
                    extra={'crawler': crawler})
        return cls(crawler, *hooks)

    def process_hook(self, *args):

        return process_chain(self.methods["process_hook"], None, *args)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings, crawler)

    def _add_hook(self, hook):
        if hasattr(hook, "process_hook"):
            self.methods["process_hook"].append(hook.process_hook)


class HookSuperManager(object):
    def __init__(self, hks: dict):
        self.hooks = hks

    @classmethod
    def from_crawler(cls, crawler):
        settings_cp = crawler.settings.copy_to_dict()
        custom_hooks = crawler.settings.getdict("SODO_HOOKS")
        for hook_module in custom_hooks:
            assert hook_module in HOOKS_LIST, "hooks name must in {} and " \
                                              "type is dict".format(HOOKS_LIST)
            SODO_HOOKS_BASE[hook_module].update(custom_hooks[hook_module])

        for hook in SODO_HOOKS_BASE:
            settings_cp[hook + '_hook'] = SODO_HOOKS_BASE[hook]

        hks = {}
        for hook_item in SODO_HOOKS_BASE:
            HookManager.component_name = hook_item + '_hook'
            crawler.settings = Settings(settings_cp)
            hks[hook_item] = HookManager.from_crawler(crawler)
        return cls(hks)


class HookABC(object):

    def engine_started(self, *args):
        self.hook_processor.hooks['engine_started'].process_hook(*args)

    def engine_stopped(self, *args):
        self.hook_processor.hooks['engine_stopped'].process_hook(*args)

    def spider_opened(self, *args):
        self.hook_processor.hooks['spider_opened'].process_hook(*args)

    def spider_idle(self, *args):
        self.hook_processor.hooks['spider_idle'].process_hook(*args)

    def spider_closed(self, *args):
        self.hook_processor.hooks['spider_closed'].process_hook(*args)

    def spider_error(self, *args):
        self.hook_processor.hooks['spider_error'].process_hook(*args)

    def request_scheduled(self, *args):
        self.hook_processor.hooks['request_scheduled'].process_hook(*args)

    def request_dropped(self, *args):
        self.hook_processor.hooks['request_dropped'].process_hook(*args)

    def request_reached_downloader(self, *args):
        self.hook_processor.hooks['request_reached_downloader'].process_hook(*args)

    def response_received(self, *args):
        self.hook_processor.hooks['response_received'].process_hook(*args)

    def response_downloaded(self, *args):
        self.hook_processor.hooks['response_downloaded'].process_hook(*args)

    def item_scraped(self, *args):
        self.hook_processor.hooks['item_scraped'].process_hook(*args)

    def item_dropped(self, *args):
        self.hook_processor.hooks['item_dropped'].process_hook(*args)

    def item_error(self, *args):
        self.hook_processor.hooks['item_dropped'].process_hook(*args)

    def _set_signals(self, crawler):
        settings = crawler.settings
        self.hook_processor = load_object(settings.get("HOOK_PROCESSOR", HOOK_PROCESSOR)).from_crawler(crawler)
        crawler.signals.connect(self.engine_started, signal=signals.engine_started)
        crawler.signals.connect(self.engine_stopped, signal=signals.engine_stopped)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(self.spider_error, signal=signals.spider_error)
        crawler.signals.connect(self.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(self.request_dropped, signal=signals.request_dropped)
        crawler.signals.connect(self.request_reached_downloader, signal=signals.request_reached_downloader)
        crawler.signals.connect(self.response_received, signal=signals.response_received)
        crawler.signals.connect(self.response_downloaded, signal=signals.response_downloaded)
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(self.item_error, signal=signals.item_error)


class HooKBase(object):
    "Base class for implementing Hook"

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_hook(self, *args, **kwargs):
        raise NotImplementedError('{}.process_hook is not defined'.format(self.__class__.__name__))

    def __call__(self, *args, **kwargs):
        return self.process_hook(*args, **kwargs)


engine_started_default_hook_cls = _default_hook("engine_started")
engine_stopped_default_hook_cls = _default_hook("engine_stopped")
spider_opened_default_hook_cls = _default_hook("spider_opened")
spider_idle_default_hook_cls = _default_hook("spider_idle")
spider_closed_default_hook_cls = _default_hook("spider_closed")
spider_error_default_hook_cls = _default_hook("spider_error")
request_scheduled_default_hook_cls = _default_hook("request_scheduled")
request_dropped_default_hook_cls = _default_hook("request_dropped")
request_reached_downloader_default_hook_cls = _default_hook("request_reached_downloader")
response_received_default_hook_cls = _default_hook("response_received")
response_downloaded_default_hook_cls = _default_hook("response_downloaded")
item_scraped_default_hook_cls = _default_hook("item_scraped")
item_dropped_default_hook_cls = _default_hook("item_dropped")
item_error_default_hook_cls = _default_hook("item_error")

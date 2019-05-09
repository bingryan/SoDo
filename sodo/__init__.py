#!/usr/bin/env python
# -*- coding: utf-8 -*-
SODO_HOOKS_BASE = {
    "engine_started": {
        "sodo.hook.engine_started_default_hook_cls": 1
    },
    "engine_stopped": {
        "sodo.hook.engine_stopped_default_hook_cls": 1
    },
    "spider_opened": {
        "sodo.hook.spider_opened_default_hook_cls": 1
    },
    "spider_idle": {
        "sodo.hook.spider_idle_default_hook_cls": 1
    },
    "spider_closed": {
        "sodo.hook.spider_closed_default_hook_cls": 1
    },
    "spider_error": {
        "sodo.hook.spider_error_default_hook_cls": 1
    },
    "request_scheduled": {
        "sodo.hook.request_scheduled_default_hook_cls": 1
    },
    "request_dropped": {
        "sodo.hook.request_dropped_default_hook_cls": 1
    },
    "request_reached_downloader": {
        "sodo.hook.request_reached_downloader_default_hook_cls": 1
    },
    "response_received": {
        "sodo.hook.response_received_default_hook_cls": 1
    },
    "response_downloaded": {
        "sodo.hook.response_downloaded_default_hook_cls": 1
    },
    "item_scraped": {
        "sodo.hook.item_scraped_default_hook_cls": 1
    },
    "item_dropped": {
        "sodo.hook.item_dropped_default_hook_cls": 1
    },
    "item_error": {
        "sodo.hook.item_error_default_hook_cls": 1
    }
}

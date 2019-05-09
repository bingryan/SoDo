#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sodo.hook import HooKBase


# 第一种方式直接继承HooKBase,然后书写hook 逻辑
class FirstLogHook(HooKBase):

    def process_hook(self, *args, **kwargs):
        # self.crawler 有全局settings
        # settings = self.crawler.settings
        print("This is First LogHook")
        print("FirstLogHook get global settings:", self.crawler.settings)


# 第二种方式,直接全套逻辑自己书写
class SecondLogHook(object):
    "Base class for implementing Hook"

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        # 初始化的参数逻辑
        return cls(crawler)

    def process_hook(self, *args, **kwargs):
        print("This is Second LogHook")
        print("SecondLogHook get global settings:", self.crawler.settings)

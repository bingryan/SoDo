# Hooks

SoDo 提供了十多种的Hook,下面是全部

```python
SODO_HOOKS = {
    "engine_started": {
        # engine_started hook
    },
    "engine_stopped": {
        # engine_stopped hook
    },
    "spider_opened": {
       # spider_opened hook
    },
    "spider_idle": {
        # spider_idle hook
    },
    "spider_closed": {
       # spider_closed hook
    },
    "spider_error": {
       # spider_error hook
    },
    "request_scheduled": {
       # request_scheduled hook
    },
    "request_dropped": {
       # request_dropped hook
    },
    "request_reached_downloader": {
       # request_reached_downloader hook
    },
    "response_received": {
       # response_received hook
    },
    "response_downloaded": {
       # response_downloaded hook
    },
    "item_scraped": {
       # item_scraped hook
    },
    "item_dropped": {
       # item_dropped hook
    },
    "item_error": {
       # item_error hook
    }
}
``` 

## 如何使用Hooks

Hook 的使用和Scrapy中的pipeline 和 Middleware 使用一样，下面就在入门教程基础上来写一个Hook,首先在`pipeline.py` 和 `middlewares.py`的同级目录下新建立一个
`hooks.py`,如下书写了两个Hook：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sodo.hook import HooKBase


# 第一种方式,直接继承HooKBase,然后在process_hook 函数中书写hook 逻辑
class FirstLogHook(HooKBase):

    def process_hook(self, *args, **kwargs):
        # self.crawler 有全局settings 
        # settings = self.crawler.settings
        print("This is First LogHook")
        print("get global settings:", self.crawler.settings)


# 第二种方式,逻辑自己书写,然后在process_hook 函数中书写hook 逻辑
class SecondLogHook(object):
    "Base class for implementing Hook"

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        # 初始化的参数逻辑
        return cls(crawler)

    def process_hook(self, *args, **kwargs):
        print("This is First LogHook")
        print("get global settings:", self.crawler.settings)
```

然后在`settings.py`中配置Hook信息，如下：

```python
SODO_HOOKS = {
    "engine_started": {
        'helloworld.hooks.FirstLogHook': 111,
    },

    "engine_stopped": {
        'helloworld.hooks.FirstLogHook': 111,
        'helloworld.hooks.SecondLogHook': 121,
    },
}
```
然后启动项目，发现在引擎启动的时候,会触发`helloworld.hooks.FirstLogHook`,然后在shutdown项目，然后发现会先触发`helloworld.hooks.FirstLogHook`,然后再触发`helloworld.hooks.SecondLogHook`,
对应的值越小越先触发。

是的，你会发现Hook可以帮我们在实际开发中解决很多问题，比如爬虫解析错误或者其他什么错误可以写一个邮件通知Hook来进行邮件处理。如果利用好将是一大利器。祝你好运！
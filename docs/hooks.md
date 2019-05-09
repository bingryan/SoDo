# Hooks

There are a lot of Hooks available, and here's all


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

## HOW TO

The use of Hook is the same as that of Pipeline and Middleware in Scrapy.Let's show you how to use it.First, create a hooks.py under the same directory of pipeline.py and middlewares.py,then,copy that code to `hooks.py` 


```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sodo.hook import HooKBase

# First, inherit HooKBase directly and write hook logic in the process_hook function


# The first way: implement HooKBase,do some logic you want  in process_hook function 
class FirstLogHook(HooKBase):

    def process_hook(self, *args, **kwargs):
        print("This is First LogHook")
        print("get global settings:", self.crawler.settings)


# The second way
class SecondLogHook(object):

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_hook(self, *args, **kwargs):
        print("This is First LogHook")
        print("get global settings:", self.crawler.settings)
```

Add some configuration information to `settings.py`


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

That's all, When you start the program, you will get logic from  `helloworld.hooks.FirstLogHook` at `engine_started`.When you shutdown.
you will get logic from `helloworld.hooks.FirstLogHook` at first, then `helloworld.hooks.SecondLogHook`.

[Tutorial Code](https://github.com/ycvbcvfu/SoDo/blob/master/examples/helloworld)

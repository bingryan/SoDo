# Filter
SoDo 在进行调度的时候，默认是提供了BloomFilter。默认设置如下：。

```python
SCHEDULER_FILTER_CLASS = 'sodo.filter.BloomFilter'
SCHEDULER_BLOOMFILTER_CAPACITY = 100000000
SCHEDULER_BLOOMFILTER_ERROR_RATE = 0.00000001
```

如果你不想要用`BloomFilter`,那么你可以改为`OriginalFilter`,设置如下

```python
SCHEDULER_FILTER_CLASS = 'sodo.filter.OriginalFilter'
```

或者继承'sodo.filter.ABCFilter'进行自定义.

对于想把BloomFilter 放在redis 的server 端,那么你可以使用[redisbloom](https://github.com/RedisLabsModules/redisbloom),然后选择为`SCHEDULER_FILTER_CLASS = 'sodo.filter.OriginalFilter'`

你的业务可能不仅仅要用url 作为指纹过滤，因为业务的多样性还和Kafka消息有关，那么设置`FINGERPRINT_BY_KAFKA_MESSAGE = True`,默认为False.
假设你爬取`www.google.com`,那么对于www.google.com/a.html 针对不同的发送消息，那么指纹也不一样。针对某些不需要过滤的，那么直接设置`dont_filter=False`可能来的更直接一点

```python
request_params = {
    "dont_filter": # 也可以加载消息逻辑来判断True or False,
}
```

当需求对`SCHEDULER_BLOOMFILTER_CAPACITY` 和 `SCHEDULER_BLOOMFILTER_ERROR_RATE` 设置的时候,那么你可能对过滤这一快有更高要求了
,你可以访问[Bloom_filter wiki](https://en.wikipedia.org/wiki/Bloom_filter)来对BloomFilter有一个更深入的了解之后进行自行配置


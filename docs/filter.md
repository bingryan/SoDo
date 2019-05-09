# Filter
The scheduler uses BloomFilter by default.

```python
SCHEDULER_FILTER_CLASS = 'sodo.filter.BloomFilter'
SCHEDULER_BLOOMFILTER_CAPACITY = 100000000
SCHEDULER_BLOOMFILTER_ERROR_RATE = 0.00000001
```

`sodo.filter.OriginalFilter` does nothing 

```python
SCHEDULER_FILTER_CLASS = 'sodo.filter.OriginalFilter'
```
You can also use [redisbloom](https://github.com/RedisLabsModules/redisbloom), when you set `SCHEDULER_FILTER_CLASS = 'sodo.filter.OriginalFilter'` at `settings.py`

for `SCHEDULER_BLOOMFILTER_CAPACITY` and `SCHEDULER_BLOOMFILTER_ERROR_RATE`,You can customize the settings by [Bloom_filter wiki](https://en.wikipedia.org/wiki/Bloom_filter)





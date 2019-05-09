# Spiders

In addition to Scrapy's existing reptiles, Kafka topic spider  are currently available.

## Scrapy Spider

Hook functionality is also available for Scrapy's built-in Spider and CrawlSpider.`sodo.spider.Spider` is equivalent to `scrapy.spiders.Spider`,
`sodo.spider.CrawlSpider` is equivalent to `scrapy.spiders.CrawlSpider`.


##  Kafka Spider

`Kafka offset autocommit`：KafkaTopicSpider 和 KafkaTopicCrawlSpider

`Kafka offset not autocommit，offset storage at Redis`：KafkaTopicAdvancedSpider 和 KafkaTopicAdvancedCrawlSpider

`Kafka offset not autocommit，offset storage at Redis,and priority partition`:KafkaTopicPriorityCrawlSpider,
KafkaTopicPrioritySpider,

### Kafka Spider base Logic

`tips:` For distributed Spiders,`SODO_KAFKA_SPIDER_GROUP_ID` must be set.

#### step1: Message Prepossessing 


```python
def message_pre_process(self, message):
	"""The return value here is used as a splicing value for the next step

	"""
    return bytes_to_json(message).get("message").get("p")
```


#### step2:Prefix stitching (optional)



request url ：`SODO_KAFKA_SPIDER_MESSAGE_PREFIX + message_pre_process retrun value` 

#### step3: request params

request_params at your spider will be request params.

```
request_params = {
    "method": 'POST',
    "dont_filter": True
}
```



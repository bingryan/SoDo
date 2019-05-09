# Spiders

`sodo` 提供了除了Scrapy 已有爬虫之外，目前还提供了基于Kafka的流式爬虫

## Scrapy 内置Spider

为了使Scrapy内置的Spider 和 CrawlSpider 也可以使用 Hook 功能。`sodo.spider.Spider`等同于`scrapy.spiders.Spider`,
`sodo.spider.CrawlSpider`等同于`scrapy.spiders.CrawlSpider`,



##  Kafka Spider
基于Kafka 的爬虫一共有六种

`Kafka offset自动提交`：KafkaTopicSpider 和 KafkaTopicCrawlSpider

`Kafka offset手动提交，offset存放Redis`：KafkaTopicAdvancedSpider 和 KafkaTopicAdvancedCrawlSpider

`Kafka offset手动提交，offset存放Redis,并提供优先队列`:KafkaTopicPriorityCrawlSpider,
KafkaTopicPrioritySpider,

### Kafka Spider 共有的逻辑

对于分布式爬虫，`必须`设置`SODO_KAFKA_SPIDER_GROUP_ID` 否则会有重复消费消息的现象.比如我们的入门案例就设置：`SODO_KAFKA_SPIDER_GROUP_ID = "ryan"`

#### step1:消息的预处理

```python
def message_pre_process(self, message):
	"""消费Kafka消息之后,对消息(传输为bytes类型)进行预处理的, 比如借助sodo.utils下工具函数进行预处理
	此处常用两个工具函数的如下：
	sodo.utils.string.bytes_to_str:当你传输的为字符串的时候，把bytes 转换为str类型
	sodo.utils.string.bytes_to_json：当传输的为json 时
	"""
    return bytes_to_json(message).get("message").get("p")
```


#### step2:消息的拼接前缀

需要在settings.py中配置`SODO_KAFKA_SPIDER_MESSAGE_PREFIX`,比如我们的入门案例就是用了`SODO_KAFKA_SPIDER_MESSAGE_PREFIX = 'https://news.ycombinator.com/news?p='`,

请求url逻辑：`SODO_KAFKA_SPIDER_MESSAGE_PREFIX + message_pre_process函数的返回值` 作为请求url

#### step3: 请求参数

对于比如有`POST`请求，或者不过滤等逻辑操作都可以在`request_params`处做文章.

```
request_params = {
    "method": 'POST',
    "dont_filter": True
}
```


### KafkaTopicSpider 和 KafkaTopicCrawlSpider

这两种爬虫提供了对kafka自动提交offfset 模式。除了请求的url 来自与Kafka 之外。
KafkaTopicSpider 等同于 Scrapy中的Spider，KafkaTopicCrawlSpider等同于CrawlSpider

### KafkaTopicAdvancedSpider 和 KafkaTopicAdvancedCrawlSpider

这两种爬虫提供了把offset 存放redis 中，目标是提供爬虫的开发也可以持续集成(CI), 比如爬虫解析页面报错，然后修复之后直接push 代码到代码仓库就完成了自动部署操作同时不丢失消息

###   KafkaTopicPrioritySpider 和 KafkaTopicPriorityCrawlSpider

Kafka 是不提供优先级别的队列的。如果你想要针对某些信息优先被消费，那么你可以设置`SODO_KAFKA_PRIORITY_PARTITION`(默认为1), 然后把你想要的优先消息发送到此Partition.


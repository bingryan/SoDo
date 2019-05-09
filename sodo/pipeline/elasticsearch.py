#!/usr/bin/env python
# -*- coding: utf-8 -*
import json
from elasticsearch import Elasticsearch
from scrapy.utils.serialize import ScrapyJSONEncoder


class ElasticSearchPipeline(object):

    def __init__(self, elasticsearch, index, doc_type):
        """
        :param elasticsearch:  elasticsearch client
        """
        self.elasticsearch = elasticsearch
        self.index = index
        self.doc_type = doc_type

    def process_item(self, item, spider):
        resource = {
            'spider': spider.name,
            'data': {
                'item': dict(item)
            }
        }
        self.elasticsearch.index(index=self.index, doc_type=self.doc_type,
                                 body=json.dumps(resource, cls=ScrapyJSONEncoder))
        return item

    @classmethod
    def from_settings(cls, settings):
        """
        :param settings: the current Scrapy settings
        :type settings: scrapy.settings.Settings

        :rtype: A :class:`~KafkaPipeline` instance
        """
        elasticsearch = Elasticsearch(settings.get('ELASTICSEARCH_PIPELINE_RFC_URLS', 'localhost:9200'))
        index = Elasticsearch(settings.get('ELASTICSEARCH_PIPELINE_INDEX', 'elasticsearch_pipeline_index'))
        doc_type = Elasticsearch(settings.get('ELASTICSEARCH_PIPELINE_DOC_TYPE'))
        doc_type = index if not doc_type else doc_type
        return cls(elasticsearch, index, doc_type)

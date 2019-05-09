import logging

from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import referer_str, request_fingerprint
from scrapy.utils.misc import load_object, create_instance
from sodo import default_settings

logger = logging.getLogger(__name__)


class RedisDupeFilter(BaseDupeFilter):
    """Redis-based Request Fingerprint duplicates filter.
    """

    logger = logger

    def __init__(self, queue=None, debug=False, logdupes=True, fingerprint_by_kafka=False):
        """
        :param queue: filter queue, you can implements sodo.filter.ABCFilter interface，then change SCHEDULER_FILTER_CLASS
        :param debug:  False for  default change DUPEFILTER_DEBUG
        :param logdupes: Logs given request, True for default,change DUPEFILTER_LOG
        """
        self.queue = queue
        self.debug = debug
        self.logdupes = logdupes
        self.fingerprint_by_kafka = fingerprint_by_kafka

    @classmethod
    def from_settings(cls, settings):
        # log
        dupefilter_debug = settings.get("DUPEFILTER_LOG", default_settings.DUPEFILTER_DEBUG)
        dupefilter_log = settings.get("DUPEFILTER_LOG", default_settings.DUPEFILTER_LOG)

        # filter key in server
        dupefilter_key = settings.get("SCHEDULER_DUPEFILTER_KEY", default_settings.SCHEDULER_DUPEFILTER_KEY)
        fingerprint_by_kafka = settings.get("FINGERPRINT_BY_KAFKA_MESSAGE", default_settings.SCHEDULER_DUPEFILTER_KEY)

        scheduler_filter_class = load_object(
            settings.get("SCHEDULER_FILTER_CLASS", default_settings.SCHEDULER_FILTER_CLASS))
        filter_queue = create_instance(scheduler_filter_class, settings, None, dupefilter_key)
        return cls(filter_queue, dupefilter_debug, dupefilter_log, fingerprint_by_kafka)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_spider(crawler.spider)

    def request_seen(self, request):
        # TODO: add topic message fingerprint
        msg_fingerprint = ""
        if self.fingerprint_by_kafka:
            msg_fingerprint = request.meta.get("topic_message")
            if msg_fingerprint is None:
                msg_fingerprint = ""
        fp = self.request_fingerprint(request) + msg_fingerprint
        if self.queue.contains(fp):
            return True
        else:
            self.queue.add(fp)
            return False

    def request_fingerprint(self, request):
        return request_fingerprint(request)

    @classmethod
    def from_spider(cls, spider):
        settings = spider.settings
        # log
        dupefilter_debug = settings.get("DUPEFILTER_LOG", default_settings.DUPEFILTER_DEBUG)
        dupefilter_log = settings.get("DUPEFILTER_LOG", default_settings.DUPEFILTER_LOG)

        # filter key in server
        dupefilter_key = settings.get("SCHEDULER_DUPEFILTER_KEY", default_settings.SCHEDULER_DUPEFILTER_KEY)
        fingerprint_by_kafka = settings.getbool("FINGERPRINT_BY_KAFKA_MESSAGE",
                                                default_settings.FINGERPRINT_BY_KAFKA_MESSAGE)

        key = dupefilter_key % {'spider': spider.name}

        scheduler_filter_class = load_object(
            settings.get("SCHEDULER_FILTER_CLASS", default_settings.SCHEDULER_FILTER_CLASS))

        filter_queue = create_instance(scheduler_filter_class, settings, None, key)
        return cls(filter_queue, dupefilter_debug, dupefilter_log, fingerprint_by_kafka)

    def close(self, reason=''):
        self.clear()

    def clear(self):
        """clear filter queue data."""
        self.queue.clear()

    def log(self, request, spider):
        if self.debug:
            msg = "Filtered duplicate request: %(request)s (referer: %(referer)s)"
            args = {'request': request, 'referer': referer_str(request)}
            self.logger.debug(msg, args, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request: %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False

        spider.crawler.stats.inc_value('dupefilter/filtered', spider=spider)

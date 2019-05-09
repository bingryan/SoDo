#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import mmh3
import random

from abc import ABCMeta
from sodo.utils.connection import client_from_settings
from sodo import default_settings


class ABCFilter(metaclass=ABCMeta):

    def add(self, val):
        """add key """
        pass

    def contains(self, val):
        """Tests a key's membership in this storage ."""
        pass

    def clear(self):
        """clear """
        pass

    def __contains__(self, val):
        """Tests a key's membership in this storage ."""
        pass


class OriginalFilter(ABCFilter):

    def __init__(self, server=None, key='OriginalFilter'):
        self.server = server
        self.key = key

    @classmethod
    def from_settings(cls, settings, key='OriginalFilter'):
        server = client_from_settings(settings)
        return cls(server, key)

    def add(self, val):
        return self.server.sadd(self.key, val)

    def contains(self, val):
        return self.add(val) == 0

    def clear(self):
        self.server.delete(self.key)

    def __contains__(self, val):
        return self.contains(val)


class BloomFilter(ABCFilter):
    """
    https://en.wikipedia.org/wiki/Bloom_filter
    """

    def __init__(self, server=None, key='BloomFilter', capacity=100000000, error_rate=0.00000001):
        """

        :param capacity: the number of inserted elements: 2^32 is ok
        :param error_rate:a desired false positive probability p (and assuming the optimal value of k is used)
        :param server:
        :param blocknum:limits bitmaps to 512MB,more info visit:https://redis.io/commands/setbit
        :param key:
        """
        self.m = math.ceil(
            -capacity * math.log(error_rate) / (math.log(2) * math.log(2)))  # the length of a Bloom filter
        self.k = math.ceil(-math.log2(error_rate))  # the corresponding number of hash func: -log2(error_rate)
        self.mem = math.ceil(self.m / 8 / 1024 / 1024)  # memory
        self.allocation_size = math.ceil(self.mem / 512)  # redis setbit: limits bitmaps to (smaller than 2^32)512MB
        self.seeds = random.sample(range(1, capacity), self.k)
        self.key = key
        self.key_set = set(key)
        self.server = server

    @classmethod
    def from_settings(cls, settings, key='BloomFilter'):
        server = client_from_settings(settings)
        capacity = settings.get("SCHEDULER_BLOOMFILTER_CAPACITY", default_settings.SCHEDULER_BLOOMFILTER_CAPACITY)
        error_rate = settings.get("SCHEDULER_BLOOMFILTER_ERROR_RATE", default_settings.SCHEDULER_BLOOMFILTER_ERROR_RATE)
        return cls(server, key, capacity, error_rate)

    def add(self, val):
        k = self.key + ":" + str(ord(val[0]) % self.allocation_size)
        self.key_set.add(k)
        values = self.make_hashes(val)
        for value in values:
            self.server.setbit(k, value, 1)

    def contains(self, val):
        """Tests a key's membership in this Bloom Filter"""
        k = self.key + ":" + str(ord(val[0]) % self.allocation_size)
        values = self.make_hashes(val)
        exist = True
        for value in values:
            exist = exist and self.server.getbit(k, value)
        return exist

    def clear(self):
        self.server.delete(*self.key_set)

    def __contains__(self, val):
        return self.contains(val)

    def make_hashes(self, key):
        res = list()
        for seed in self.seeds:
            hash_value = mmh3.hash(key, seed)  # 32 bit signed int
            res.append(hash_value % (2 ** 32))  # max_value:2 ** 32, and bit offset must be an integer
        return res

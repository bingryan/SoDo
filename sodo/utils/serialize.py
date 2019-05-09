#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle


class PickleSerializer(object):

    @classmethod
    def loads(cls, s):
        return pickle.loads(s)

    @classmethod
    def dumps(cls, obj):
        return pickle.dumps(obj, protocol=-1)

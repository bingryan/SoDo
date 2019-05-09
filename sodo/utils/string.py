#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import ast


def bytes_to_str(s, encoding='utf-8'):
    """Returns a str if a bytes object is given.

    >>> 'example' == bytes_to_str(b"example")
    True
    """
    if isinstance(s, bytes):
        value = s.decode(encoding)
    else:
        value = s
    return value


def str_to_bytes(s, encoding='utf-8'):
    """Returns a bytes if a string object is given.

    >>> b"example" == str_to_bytes('example')
    True
    """

    if isinstance(s, str):
        value = s.encode(encoding)
    else:
        value = s
    return value


def json_to_bytes(obj):
    """
    >>> obj = {'id': '6fa459ea-ee8a-3ca4-894e-db77e160355e', 'data': {'item': {'one': 1, 'two': 2, 'three': {'three.1': 3.1, 'three.2': 3.2}}}}
    >>> json_to_bytes_res = json_to_bytes(obj)
    >>> json_to_bytes_res == b'{"id": "6fa459ea-ee8a-3ca4-894e-db77e160355e", "data": {"item": {"one": 1, "two": 2, "three": {"three.1": 3.1, "three.2": 3.2}}}}'
    :param obj:
    :return: bytes
    """
    return str_to_bytes(json.dumps(obj))


def bytes_to_json(obj):
    """
    >>> obj = b'{"id": "6fa459ea-ee8a-3ca4-894e-db77e160355e", "data": {"item": {"one": 1, "two": 2, "three": {"three.1": 3.1, "three.2": 3.2}}}}'
    >>> bytes_to_json_res = bytes_to_json(obj)
    >>> bytes_to_json_res == {'id': '6fa459ea-ee8a-3ca4-894e-db77e160355e', 'data': {'item': {'one': 1, 'two': 2, 'three': {'three.1': 3.1, 'three.2': 3.2}}}}
    :param obj:
    :return:json
    """
    return ast.literal_eval(bytes_to_str(obj))


if __name__ == '__main__':
    import doctest

    doctest.testmod()

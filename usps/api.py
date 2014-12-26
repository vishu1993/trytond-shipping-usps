# -*- coding: utf-8 -*-
"""
    api.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import requests
from lxml.builder import E
from exceptions import USPSException


class BaseAPI(object):
    """
    Base client class to be subclassed by all API methods.

    :param username: API Username
    :param password: API Password
    :param is_test: True if supposed to work in test mode
    """

    urls = {
        'secure': 'https://secure.shippingapis.com/ShippingAPI.dll',
        'unsecure': 'http://production.shippingapis.com/ShippingAPITest.dll',
    }

    def __init__(self, username, password, is_test=True):
        self.username = username
        self.password = password
        self.is_test = is_test

    def send_request(self, url, api_type, data_xml):
        """
        Sends data to the server on a request
        """
        params = {
            'API': api_type,
            'XML': data_xml,
        }
        rv = requests.get(url, params=params)
        return rv.content

    @classmethod
    def make_elements(cls, required_keys, args, kwargs):
        """Ensures that the given keys exist in either the elements list given
        by args or exist as keys in the kwargs (with their values). The kwargs
        are converted into elements with tags as their keys and the text as the
        value provided in the dict. Then the elements in args and kwargs are
        combined into a list and returned

        :param required_keys: An iterable of the required Keys
        :param kwargs: A dictionary of the key:value pairs to make elements
        :param args: A list of elements as positional args. Their tag attribute
            will be evaluated to check for existance
        :return: a list of lxml Elements made out of key value pairs and args
        >>> BaseAPI.make_elements(['a', 'b'], [], {'a': '1', 'b': '2'})
        [<Element a at 0x...>, <Element b at 0x...>]
        >>> BaseAPI.make_elements(['a', 'b'], [E.b('2')], {'a': '1'})
        [<Element a at 0x...>, <Element b at 0x...>]
        >>> BaseAPI.make_elements(['a', 'b'], [], {'a': '1',})
        Traceback (most recent call last):
            ...
        ValueError: Attributes b is/are required.
        >>> BaseAPI.make_elements(['a', 'b', 'c'], [], {'a': '1',})
        Traceback (most recent call last):
            ...
        ValueError: Attributes c,b is/are required.
        """
        keys_set = frozenset(required_keys)
        args_keys = frozenset([e.tag for e in args])
        dict_keys_set = frozenset(kwargs.keys())

        # Diff = required_keys - elements in args - elements in the kwargs
        difference = keys_set.difference(args_keys).difference(dict_keys_set)

        if difference:
            raise ValueError(
                'Attributes %s is/are required.' % ','.join(difference)
            )

        return [E(k, v) for k, v in kwargs.iteritems()] + list(args)

    def look_for_error(self, response):
        """Looks for an element error and raises an :exception:`USPSException`
        out of it, which could be handled by applications using this API.
        """
        if response.tag == 'Error':
            raise USPSException("%s-%s:%s" % (
                response.Source,
                response.Number,
                response.Description,
            ), response)

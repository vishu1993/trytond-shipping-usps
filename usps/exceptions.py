# -*- coding: utf-8 -*-
"""
    exception.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""


class USPSException(Exception):
    """
    Exceptions in USPS core response
    """
    pass


class USPSInvalidAddress(Exception):
    """
    Invalid Address for USPS
    """
    pass


class USPSInvalidZip5(Exception):
    """
    Invalid Zip5 for USPS
    """
    pass

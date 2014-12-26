# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from carrier import CarrierConfig
from configuration import USPSConfiguration
from trytond.pool import Pool
from party import Address


def register():
    Pool.register(
        Address,
        CarrierConfig,
        USPSConfiguration,
        module='shipping_usps', type_='model'
    )

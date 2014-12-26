# -*- coding: utf-8 -*-
"""
    carrier

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
from trytond.pool import PoolMeta

__all__ = ['CarrierConfig']
__metaclass__ = PoolMeta


class CarrierConfig:
    "Carrier Configuration"
    __name__ = 'carrier.configuration'

    @classmethod
    def get_default_validation_providers(cls):
        """
        Add usps to validation provider list
        """
        methods = super(CarrierConfig, cls).get_default_validation_providers()
        methods.append(('usps', 'USPS'))
        return methods

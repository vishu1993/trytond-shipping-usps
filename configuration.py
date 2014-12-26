# -*- coding: utf-8 -*-
"""
    configuration.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import fields, ModelSingleton, ModelSQL, ModelView
from usps.address_validation import AddressValidation
from usps.city_state_lookup import CityStateLookup

__all__ = ['USPSConfiguration']


class USPSConfiguration(ModelSingleton, ModelSQL, ModelView):
    """
    Configuration settings for USPS
    """
    __name__ = 'usps.configuration'

    username = fields.Char('USPS Username', required=True)
    password = fields.Char('USPS User Password', required=True)
    is_test = fields.Boolean('Is Test')

    def get_api_instance_of(self, call):
        """
        Return API Instance according to type
        """
        if call == 'address_val':
            return AddressValidation(self.username, self.password, self.is_test)
        elif call == 'city_state_lookup':
            return CityStateLookup(self.username, self.password, self.is_test)

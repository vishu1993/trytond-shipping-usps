# -*- coding: utf-8 -*-
"""
    test_base

    Test usps Integration

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
import os

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.config import CONFIG
CONFIG['data_path'] = '.'


class TestUSPSBase(unittest.TestCase):
    """Test USPS Integration
    """

    def setUp(self):
        trytond.tests.test_tryton.install_module('shipping_usps')
        self.Address = POOL.get('party.address')
        self.USPSConfiguration = POOL.get('usps.configuration')
        self.CarrierConfig = POOL.get('carrier.configuration')
        self.Party = POOL.get('party.party')
        self.PartyContact = POOL.get('party.contact_mechanism')
        self.Country = POOL.get('country.country')
        self.CountrySubdivision = POOL.get('country.subdivision')
        self.Currency = POOL.get('currency.currency')
        self.Company = POOL.get('company.company')
        self.User = POOL.get('res.user')

        assert 'USPS_USERNAME' in os.environ, \
            "USPS_USERNAME not given. Hint:Use export USPS_USERNAME=<username>"
        assert 'USPS_PASSWORD' in os.environ, \
            "USPS_PASSWORD not given. Hint:Use export USPS_PASSWORD=<password>"

    def setup_defaults(self):
        """Method to setup defaults
        """
        # Create currency
        self.currency, = self.Currency.create([{
            'name': 'United Stated Dollar',
            'code': 'USD',
            'symbol': 'USD',
        }])
        self.Currency.create([{
            'name': 'Indian Rupee',
            'code': 'INR',
            'symbol': 'INR',
        }])

        country_us, = self.Country.create([{
            'name': 'United States',
            'code': 'US',
        }])

        subdivision_florida, = self.CountrySubdivision.create([{
            'name': 'Florida',
            'code': 'US-FL',
            'country': country_us.id,
            'type': 'state'
        }])

        subdivision_california, = self.CountrySubdivision.create([{
            'name': 'California',
            'code': 'US-CA',
            'country': country_us.id,
            'type': 'state'
        }])

        with Transaction().set_context(company=None):
            company_party, = self.Party.create([{
                'name': 'Test Party',
                'vat_number': '123456',
                'addresses': [('create', [{
                    'name': 'Amine Khechfe',
                    'street': '247 High Street',
                    'zip': '94301-1041',
                    'city': 'Palo Alto',
                    'country': country_us.id,
                    'subdivision': subdivision_california.id,
                }])]
            }])

        # USPS Configuration
        self.USPSConfiguration.create([{
            'username': os.environ['USPS_USERNAME'],
            'password': os.environ['USPS_PASSWORD'],
            'is_test': True,
        }])
        self.CarrierConfig.create([{
            'default_validation_provider': 'usps',
        }])
        self.company, = self.Company.create([{
            'party': company_party.id,
            'currency': self.currency.id,
        }])
        self.PartyContact.create([{
            'type': 'phone',
            'value': '8005551212',
            'party': self.company.party.id
        }])

        self.User.write(
            [self.User(USER)], {
                'main_company': self.company.id,
                'company': self.company.id,
            }
        )

        self.address_val = self.USPSConfiguration(1).get_api_instance_of(
            'address_val'
        )
        self.city_state_lookup = self.USPSConfiguration(1).get_api_instance_of(
            'city_state_lookup'
        )

        CONTEXT.update(self.User.get_preferences(context_only=True))

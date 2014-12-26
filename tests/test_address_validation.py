# -*- coding: utf-8 -*-
"""
    test_address_validation

    Test address validation

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: GPLv3, see LICENSE for more details.
"""
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import DB_NAME, USER, CONTEXT
from trytond.exceptions import UserError
from trytond.transaction import Transaction

from test_base import TestUSPSBase


class TestAddressValidation(TestUSPSBase):
    "Test Address Validation"

    def test_0010_address_validation(self):
        """
        Test address validation with usps
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            country_us, = self.Country.search([('code', '=', 'US')])

            subdivision_florida, = self.CountrySubdivision.search(
                [('code', '=', 'US-FL')]
            )
            subdivision_california, = self.CountrySubdivision.search(
                [('code', '=', 'US-CA')]
            )

            # Correct Address
            suggestions = self.Address(**{
                'name': 'John Doe',
                'street': '250 NE 25th St',
                'streetbis': '',
                'zip': '33141',
                'city': 'Miami Beach',
                'country': country_us.id,
                'subdivision': subdivision_florida.id,
            }).validate_address()
            self.assertEqual(suggestions, True)

            # Wrong subdivision
            suggestions = self.Address(**{
                'name': 'John Doe',
                'street': '250 NE 25th St',
                'streetbis': '',
                'zip': '33141',
                'city': 'Miami Beach',
                'country': country_us.id,
                'subdivision': subdivision_california.id,
            }).validate_address()
            self.assertTrue(len(suggestions), 1)
            self.assertEqual(suggestions[0].subdivision, subdivision_florida)

            # Wrong city and subdivision
            suggestions = self.Address(**{
                'name': 'John Doe',
                'street': '250 NE 25th St',
                'streetbis': '',
                'zip': '33141',
                'city': '',
                'country': country_us.id,
                'subdivision': subdivision_california.id,
            }).validate_address()
            self.assertEqual(len(suggestions), 1)
            self.assertEqual(suggestions[0].subdivision, subdivision_florida)

    def test_0020_address_validation_errors(self):
        """
        Test address validation usps errors
        """
        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            country_in, = self.Country.create([{
                'name': 'India',
                'code': 'IN',
            }])

            country_us, = self.Country.search([('code', '=', 'US')])

            subdivision_california, = self.CountrySubdivision.search(
                [('code', '=', 'US-CA')]
            )

            subdivision_del, = self.CountrySubdivision.create([{
                'name': 'Delhi',
                'code': 'IN-DL',
                'country': country_in.id,
                'type': 'state'
            }])

            # India Address
            address = self.Address(**{
                'name': 'John Doe',
                'street': 'NSEZ',
                'streetbis': '',
                'zip': '110006',
                'city': 'Delhi',
                'country': country_in.id,
                'subdivision': subdivision_del.id,
            })
            self.assertRaises(UserError, address.validate_address)

            # Correct subdivision doesn't exist
            suggestions = self.Address(**{
                'name': 'John Doe',
                'street': '264 Stirling Road',
                'streetbis': '',
                'zip': '04864',
                'city': 'Warren',
                'country': country_us.id,
                'subdivision': subdivision_california.id,
            }).validate_address()
            self.assertEqual(len(suggestions), 0)

            # Wrong ZIP
            address = self.Address(**{
                'name': 'John Doe',
                'street': '250 NE 25th St',
                'streetbis': '',
                'zip': 'XXXXX',  # Wrong ZIP
                'city': 'Miami Beach',
                'country': country_us.id,
                'subdivision': subdivision_california.id,
            })
            self.assertRaises(UserError, address.validate_address)


def suite():
    suite = trytond.tests.test_tryton.suite()
    from trytond.modules.account.tests import test_account
    for test in test_account.suite():
        if test not in suite:
            suite.addTest(test)
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestUSPSBase)
    )
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

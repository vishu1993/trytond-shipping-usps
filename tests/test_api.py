# -*- coding: utf-8 -*-
"""
    tests/test_api.py

    :copyright: (C) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import os
import unittest

from usps.address_validation import AddressValidation
from usps.city_state_lookup import CityStateLookup
from usps.exceptions import USPSInvalidAddress, USPSInvalidZip5


class TestUSPSApi(unittest.TestCase):
    """
    Test USPS API
    """
    @classmethod
    def setUpClass(self):
        """Check if the variables for initialising the test case is available
        in the environment"""
        assert 'USPS_USERNAME' in os.environ, \
            "USPS_USERNAME not given. Hint:Use export USPS_USERNAME=<username>"
        assert 'USPS_PASSWORD' in os.environ, \
            "USPS_PASSWORD not given. Hint:Use export USPS_PASSWORD=<password>"

    def setUp(self):
        """Initialise a AddressValidation.
        """
        self.address_validation = AddressValidation(
            os.environ['USPS_USERNAME'],
            os.environ['USPS_PASSWORD'],
            True            # Test must be performed in sandbox anyway
        )
        self.city_state_lookup = CityStateLookup(
            os.environ['USPS_USERNAME'],
            os.environ['USPS_PASSWORD'],
            True            # Test must be performed in sandbox anyway
        )

    def test_010_address_validation_true(self):
        "Test the address validation of correct address"
        # Fix wrong zip
        address_validation_type = AddressValidation.address_request_type(
            Address1='6406 Ivy Lane',
            Address2='',
            City="Greenbelt",
            State="MD",
            Zip5="20770"
        )

        response = self.address_validation.request(address_validation_type)
        self.assertEqual(response.Address.Zip5, 20770)
        self.assertEqual(response.Address.Zip4, 1441)

        # Fix city and state based on zip
        address_validation_type = AddressValidation.address_request_type(
            Address1='6406 Ivy Lane',
            Zip5="20770"
        )

        response = self.address_validation.request(address_validation_type)
        self.assertEqual(response.Address.City, 'GREENBELT')
        self.assertEqual(response.Address.State, 'MD')
        self.assertEqual(response.Address.Zip5, 20770)
        self.assertEqual(response.Address.Zip4, 1441)

    def test_020_address_validation_error(self):
        """
        Test the address validation of incomplete address. This should raise
        an error.
        """
        address_validation_type = AddressValidation.address_request_type(
            FirmName='John Doe',
            Zip5="06371"
        )

        self.assertRaises(
            USPSInvalidAddress, self.address_validation.request,
            address_validation_type
        )

    def test_030_city_state_lookup(self):
        "Test the city state lookup"
        zipcode_request_type = CityStateLookup.zipcode_request_type(
            Zip5="20770"
        )

        response = self.city_state_lookup.request(zipcode_request_type)
        self.assertEqual(response.ZipCode.Zip5, 20770)
        self.assertEqual(response.ZipCode.City, 'GREENBELT')
        self.assertEqual(response.ZipCode.State, 'MD')

    def test_030_city_state_lookup_error(self):
        "Test the city state lookup"
        zipcode_request_type = CityStateLookup.zipcode_request_type(
            Zip5="2A77"  # Invalid ZIP5
        )

        self.assertRaises(
            USPSInvalidZip5, self.city_state_lookup.request,
            zipcode_request_type
        )


def suite():
    "Create a test suite and return it for better manageability"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestUSPSApi)
    )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

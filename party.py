# -*- coding: utf-8 -*-
"""
    party.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool, PoolMeta
from usps.exceptions import USPSInvalidZip5

__all__ = ['Address']
__metaclass__ = PoolMeta


class Address:
    '''
    Address
    '''
    __name__ = 'party.address'

    @classmethod
    def __setup__(cls):
        super(Address, cls).__setup__()
        cls._error_messages.update({
            'usps_invalid_country':
                'USPS address validation not available for %s.'
        })

    def _usps_address_validate(self):
        """
        Validates the address using the USPS API.
        .. tip::
            This method is not intended to be called directly. It is
            automatically called by the address validation API of
            trytond-shipping module.
        """
        USPSConfiguration = Pool().get('usps.configuration')
        Subdivision = Pool().get('country.subdivision')
        Address = Pool().get('party.address')

        api_instance = USPSConfiguration(1).get_api_instance_of(
            'city_state_lookup'
        )

        if self.country and self.country.code != 'US':
            # XXX: Either this or assume it is the US of A
            self.raise_user_error('usps_invalid_country', self.country.name)

        zipcode_request_type = api_instance.zipcode_request_type(
            Zip5=self.zip[:5]
        )

        try:
            lookup_response = api_instance.request(zipcode_request_type)
        except USPSInvalidZip5, exc:
            self.raise_user_error(unicode(exc[0]))

        # The approach here is to check if some diff in suggestion or not,
        # If yes Return unsaved active record as suggestion else True

        try:
            subdivision, = Subdivision.search([
                ('code', '=', '%s-%s' % (
                    self.country.code, lookup_response.ZipCode.State
                ))
            ])
        except ValueError:
            # If a unique match cannot be found for the subdivision,
            # we wont be able to save the address anyway.
            return []

        suggested_address = Address(
            name=self.name,
            street=self.street,
            streetbis=self.streetbis,
            city=str(lookup_response.ZipCode.City),
            zip=str(lookup_response.ZipCode.Zip5),
            subdivision=subdivision,
            country=self.country,
        )

        if self.get_full_address(None).upper() == \
                suggested_address.get_full_address(None).upper():
            # USPS return same address if address is passed.
            return True

        return [suggested_address]

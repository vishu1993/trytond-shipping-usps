# -*- coding: utf-8 -*-
"""
    city_state_lookup.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from lxml import etree, objectify
from lxml.builder import E

from api import BaseAPI
from exceptions import USPSInvalidZip5


class CityStateLookup(BaseAPI):
    "Implements the City/State Lookup"

    @classmethod
    def zipcode_request_type(cls, Zip5, id='0'):
        """
        Builds a ZipCode xml from the given values

        API Docs:
        https://www.usps.com/business/web-tools-apis/address-information-api.htm

        Request:
            <CityStateLookupRequest USERID="xxxxxxxxxxxx">
                <ZipCode ID= "0">
                    <Zip5>90210</Zip5>
                </ZipCode>
            </CityStateLookupRequest>

        Response:
            <?xml version="1.0"?>
            <CityStateLookupResponse>
                <ZipCode ID="0">
                    <Zip5>90210</Zip5>
                    <City>BEVERLY HILLS</City>
                    <State>CA</State>
                </ZipCode>
            </CityStateLookupResponse>

        :param Zip5: U.S. city to be validated.
        """
        return E.ZipCode(E.Zip5(Zip5), ID=id)

    def look_for_error(self, response):
        """
        Look for city state lookup specific errors in response
        """
        super(CityStateLookup, self).look_for_error(response)

        # Look for address specific error
        try:
            error = response.ZipCode.Error
        except AttributeError:
            return None
        else:
            raise USPSInvalidZip5("%s-%s:%s" % (
                error.Source,
                error.Number,
                error.Description,
            ), response)

    def request(self, zipcode_type):
        """
        Calls up USPS and send the request. Get the returned response and
            return an element built out of it.

        :param address_type: lxml element with data for the address request
            type
        """
        full_zipcode_type = E.CityStateLookupRequest(
            zipcode_type, USERID=self.username
        )
        full_request = etree.tostring(full_zipcode_type)

        # Send the request
        result = self.send_request(
            self.urls['unsecure'],  # CityStateLookup API call is available on
                                    # unsecure protocol only.
            api_type='CityStateLookup',
            data_xml=full_request
        )
        response = objectify.fromstring(result)
        self.look_for_error(response)
        return response

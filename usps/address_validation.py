# -*- coding: utf-8 -*-
"""
    api.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from collections import OrderedDict
from lxml import etree, objectify
from lxml.builder import E

from api import BaseAPI
from exceptions import USPSInvalidAddress


class AddressValidation(BaseAPI):
    "Implements the Address Validation"

    @classmethod
    def address_request_type(cls, id='0', **kwargs):
        """
        Builds a AddressValidation xml from the given lxml elements

        API Docs:
        https://www.usps.com/business/web-tools-apis/address-information-api.htm

        Request:
            <AddressValidateRequest USERID="xxxxxxx">
                <Address ID="0">
                    <FirmName>XYZ Corp.</FirmName>
                    <Address1></Address1>
                    <Address2>6406 Ivy </Address2>
                    <City>Greenbelt</City>
                    <State>MD</State>
                    <Zip5></Zip5>
                    <Zip4></Zip4>
                </Address>
            </AddressValidateRequest>

        Response:
            <AddressValidateResponse>
                <Address ID="0">
                    <FirmName>XYZ Corp.</FirmName>
                    <Address2>6406 IVY LN</Address2>
                    <City>GREENBELT</City>
                    <State>MD</State>
                    <Zip5>20770</Zip5>
                    <Zip4>1441</Zip4>
                </Address>
            </AddressValidateResponse>

        :param FirmName: U.S. city to be validated. (A valid city/state/postal
                    code combination must be included as input)
        :param Address1: State to be validated. (A valid
                                  city/state/postal code combination must be
                                  included as input)
        :param Address2: Country code 2 Digits
        :param City: Postal code
        :param State: Postal code
        ::
        """
        # USPS excpected elements to be in order
        values = OrderedDict((
            ('FirmName', ''),
            ('Address1', ''),
            ('Address2', ''),
            ('City', ''),
            ('State', ''),
            ('Zip5', ''),
            ('Zip4', ''),
        ))
        values.update(kwargs)
        elements = cls.make_elements([], [], values)
        return E.Address(*elements, ID=id)

    def look_for_error(self, response):
        """
        Look for address specific errors in response
        """
        super(AddressValidation, self).look_for_error(response)

        # Look for address specific error
        try:
            error = response.Address.Error
        except AttributeError:
            return None
        else:
            raise USPSInvalidAddress("%s-%s:%s" % (
                error.Source,
                error.Number,
                error.Description,
            ), response)

    def request(self, address_type):
        """
        Calls up USPS and send the request. Get the returned response and
            return an element built out of it.

        :param address_type: lxml element with data for the address request
            type
        """
        full_address_type = E.AddressValidateRequest(
            address_type, USERID=self.username
        )
        full_request = etree.tostring(full_address_type)

        # Send the request
        result = self.send_request(
            self.urls['secure'],
            api_type='Verify',
            data_xml=full_request
        )
        response = objectify.fromstring(result)
        self.look_for_error(response)
        return response

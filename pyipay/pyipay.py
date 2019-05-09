# -*- coding: utf-8 -*-
import time
import xml.etree.ElementTree as ET
from urllib import parse
from iso4217 import Currency

from .util import Action
from .util import decrypt_payload as decrypt
from .util import encrypt_payload as encrypt
from .util import read_resource_file, sanitize, validate_gw_url
from .util import check_if_set, LANG_LOOKUP

from .exceptions import InvalidGatewayResponse


class Gateway:
    """A class that represents a payment gateway for hosted transactions, using the resource kit.
    
       The first step is to initialize the gateway by providing it the configuration received
       from the bank. This configuration consists of the following:
       
       - A resource file (called resource.cgn), which is an encrypted file that contains
         connection and credentials for the gateway.
         
       - A keystore file (called keystore.bin), which is a Java keystore that contains
         the encrption key which is used to decrypt the resource file.
         
       - The alias, which is a string. This is the friendly name of your terminal as
         setup by the bank. It it used to extract the correct configuration from the
         resource file.
    
       In addition to the above three values, you must also pass in the amount
       that you want to charge the customer for this transaction.

       :param str keystore: The file system path to the keystore file (normally called keystore.bin)
       :param str resource: The file system path to the resource file (normally called resource.cgn)
       :param str alias: The terminal alias that is to be used.
       :param float amount: The amount that needs to be charged. 3 decimal places by default for KWD.

       The following can be optionally specified, but are set to reasonable defaults:

       :param str lang: The language which will be used for the hosted pages to the end user. Values are 'en' (for English), and 'ar' for Arabic. The default is 'en'
       :param str currency: The ISO currency code. Defaults to 'KWD'. If you change this, make sure the terminal supports the currency.
       :param str tracking_id: This is a unique id for each transaction that is required by the gateway. If not supplied, the current timestamp is used.

       Once you have created an instance of the Gateway, you can specify further configuration. There are two pieces of information that are
       critical, the response url and the error url.

       These urls cannot have any query strings or fragments; and must be publicly accessible as this is where the gateway will return the results
       of the transactions.

       Finally, you request the redirect url from the module; which is where you should redirect the customer to start the payment process.

       The example provides details on how this all works:

       :Example:

       >>> from pyipay import Gateway
       >>> resource_file = r'/home/me/resource.cgn'
       >>> keystore_file = r'/home/me/keystore.bin'
       >>> gw = Gateway(keystore_file, resource_file, 'alias', 4.546)
       >>> gw.response_url = 'https://example.com/response'
       >>> gw.error_url = 'https://example.com/error'
       >>> url = gw.generate_purchase_request()
    
    """

    def __init__(
        self,
        keystore,
        resource,
        alias,
        amount,
        lang="en",
        currency='KWD',
        tracking_id=None,
    ):

        self.lang = LANG_LOOKUP.get(lang, 'USA')
        self.currency = Currency(currency).number
        self.amount = amount

        # Configure the terminal settings
        terminal_configuration = read_resource_file(resource, keystore, alias)
        root = ET.fromstring(terminal_configuration)
        terminal = {c.tag: c.text for c in root}

        self.password = terminal["password"]
        self.key = terminal["resourceKey"]
        self.portal_id = terminal["id"]
        self._pgw_url = terminal["webaddress"]

        if tracking_id is None:
            now = int(time.time())
            self.tracking_id = f"{now}"

        # Setting these as private, since we will manipulate the values
        # and sanitize them before setting the final value

        self._udf1 = self._udf2 = self._udf3 = self._udf4 = self._udf5 = ""
        self._response_url = None
        self._error_url = None

    def get_udf1(self):
        return self._udf1

    def set_udf1(self, s):
        self._udf1 = sanitize(s)

    def get_udf2(self):
        return self._udf2

    def set_udf2(self, s):
        self._udf2 = sanitize(s)

    def get_udf3(self):
        return self._udf3

    def set_udf3(self, s):
        self._udf3 = sanitize(s)

    def get_udf4(self):
        return self._udf4

    def set_udf4(self, s):
        self._udf4 = sanitize(s)

    def get_udf5(self):
        return self._udf5

    def set_udf5(self, s):
        self._udf5 = sanitize(s)

    def set_response_url(self, s):
        self._response_url = validate_gw_url(s)

    def set_error_url(self, s):
        self._error_url = validate_gw_url(s)

    def get_response_url(self):
        return self._response_url

    def get_error_url(self):
        return self._error_url

    udf1 = property(
        get_udf1, set_udf1, None, "Set and retrieve UDF1, the values are sanitized."
    )
    udf2 = property(
        get_udf2, set_udf2, None, "Set and retrieve UDF2, the values are sanitized."
    )
    udf3 = property(
        get_udf3, set_udf3, None, "Set and retrieve UDF3, the values are sanitized."
    )
    udf4 = property(
        get_udf4, set_udf4, None, "Set and retrieve UDF4, the values are sanitized."
    )
    udf5 = property(
        get_udf5, set_udf5, None, "Set and retrieve UDF5, the values are sanitized."
    )
    response_url = property(
        get_response_url, set_response_url, None, "Set and retrieve the response URL"
    )
    error_url = property(
        get_error_url, set_error_url, None, "Set and retrieve the error URL"
    )

    def _build_param_dict(self, action):
        params = []
        if action == 1:
            params.extend(
                [
                    ("action", action),
                    ("id", self.portal_id),
                    ("password", self.password),
                    ("langid", self.lang),
                    ("currencycode", self.currency),
                    ("trackid", self.tracking_id),
                    ("amt", self.amount),
                    ("udf1", self.udf1),
                    ("udf2", self.udf2),
                    ("udf3", self.udf3),
                    ("udf4", self.udf4),
                    ("udf5", self.udf5),
                    ("responseURL", self.response_url),
                    ("errorURL", self.error_url),
                ]
            )

        return dict(params)

    def _build_payload(self, action):
        params = self._build_param_dict(action.value)

        # filter out empty values, and set `safe` to avoid
        # encoding URLs, which is not supported by the platform.
        d = parse.urlencode({k: v for k, v in params.items() if v}, safe=":/")

        payload = encrypt(d, self.key)
        return payload.decode("utf-8")

    def _get_redirect_url(self, action):
        payload = self._build_payload(action.value)
        pgw_url = self._pgw_url
        gw_url = f"{pgw_url}/PaymentHTTP.htm?param=paymentInit&trandata={payload}"
        gw_url = f"{gw_url}&tranportalId={self.portal_id}&responseURL={self.response_url}&errorURL={self.error_url}"
        return gw_url

    def _parse_response(self, raw_response):
        results = parse.parse_qs(raw_response)
        try:
            encrypted_payload = results.pop("trandata")
        except KeyError:
            raise InvalidGatewayResponse("Invalid response from the gateway, missing encrypted data")
        decrypted_results = parse.parse_qs(decrypt(encrypted_payload[0], self.key))
        return results, decrypted_results

    def get_result(self, response):
        common, decrypted = self._parse_response(response)
        d = {k: v[0] for k, v in common.items()}
        for k, v in decrypted.items():
            if k not in d:
                d[k] = v[0]
        return d

    @check_if_set(['response_url', 'error_url'])
    def generate_purchase_request(self):
        redirect_to = self._get_redirect_url(Action.PURCHASE)
        return redirect_to

# -*- coding: utf-8 -*-
import binascii
import io
from enum import Enum
from urllib import parse
from zipfile import ZipFile
from functools import wraps

import jks
import pyDes
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding

from .exceptions import InvalidAlias, InvalidUrl, KeyNotFound

PADDING_OFFSET = 16
FILTER_CHARS = "!#$%^&*()+[]\\';,{}|\":<>?~`"


class Action(Enum):
    """Maps codes to more usable values."""
    PURCHASE = 1
    REFUND = 2
    VOID = 3
    INQUIRY = 8

LANG_LOOKUP = {'en': 'USA', 'ar': 'ARA'}


def validate_gw_url(s):
    """The gateway only supports http and https, and response urls cannot have query strings
       
       :raises InvalidUrl:
       :returns: the passed in url
    """
    u = parse.urlparse(s)
    if u.scheme not in ["http", "https"]:
        raise InvalidUrl("Scheme should be http or https")
    if u.query:
        raise InvalidUrl("URL cannot have a query string")
    return s


def sanitize(text):
    """Strips invalid characters from fields. Used for user defined fields (udf)s
       
       :returns: the passed in value, translated by removing `FILTER_CHARS`
    """
    return text.strip().translate(None, FILTER_CHARS)


def load_keystore(keystore_path, key_name="pgkey", passphrase="password"):
    """Loads the keystore and extracts the `pgkey` value.

       :raises KeyNotFound:

    """
    ks = jks.KeyStore.load(keystore_path, passphrase)
    try:
        pk = ks.secret_keys[key_name]
    except KeyError:
        raise KeyNotFound()
    return pk.key


def read_resource_file(resource_path, keystore_path, alias):
    """Read and returns the terminal configuration from the resource file
       which is a xml string.

       :param str resource_path: A fully qualified file system path to the resource file
       :param str keystore_path: A fully qualified file system path to the keystore file
       :param str alias: The terminal alias which is to be extracted
       :raises InvalidAlias:
       :raises BadZipFile:
       :return: terminal parameters
       :rtype: string

    """
    crypto = pyDes.triple_des(
        load_keystore(keystore_path), pyDes.ECB, padmode=pyDes.PAD_PKCS5
    )
    with open(resource_path, "rb") as f:
        resource_data = crypto.decrypt(f.read())
    temp_file = io.BytesIO(
        resource_data
    )  # a "file" that allows data to be open by ZipFile
    zip_data = ZipFile(temp_file)
    if f"{alias}.xml" not in zip_data.namelist():
        raise InvalidAlias(
            f"The alias {alias} does not exist in the resource file; {zip_data.namelist()}"
        )
    zip_contents = crypto.decrypt(zip_data.read(f"{alias}.xml"))
    return zip_contents


def encrypt_payload(plain_text, key):
    """Encrypts and returns cryptext given the plain text and key
    
       :param str plain_text: the plain text to be encrypted
       :param str key: The key, which is used for AES encryption
       :return: encrypted text
    """
    key = key.encode("utf-8")
    crypt = AES.new(key, AES.MODE_CBC, iv=key)
    return binascii.hexlify(
        crypt.encrypt(Padding.pad(plain_text.encode("utf-8"), PADDING_OFFSET))
    )


def decrypt_payload(encrypted_text, key):
    """Decrypts and returns plain text
       
       :param str encrypted_text:
       :param str key:

       :returns: plain text
    """
    key = key.encode("utf-8")
    raw = binascii.unhexlify(encrypted_text)
    crypt = AES.new(key, AES.MODE_CBC, iv=key)
    return Padding.unpad(crypt.decrypt(raw), PADDING_OFFSET).decode("utf-8")


def check_if_set(props):
    """A decorator that checks if attributes of an instance are set, before a method is called"""
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *f_args, **f_kwargs):
            if all(getattr(self, i) for i in props):
                f(self, *f_args, **f_kwargs)
            else:
                prop_str = ','.join(props)
                raise AttributeError(f'{prop_str} must be set before {f.__name__} can be called')
        return wrapped

    return wrapper

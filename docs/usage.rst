=====
Usage
=====

Requirements
============

In order to use the integration kit, you need to make sure you have the following three items:

* The resource file
* The keystore file
* The alias for the terminal

You also need to setup a web application to receive the return hooks from
the service.

You can use `https://knet-debugger.herokuapp.com/`, which is a simple website that just dumps whatever is sent to it.

Workflow
========

The payment process involves HTML redirection. This kit provides the redirection target, and the code you can use
to decrypt the results.

The first step is to generate the redirection url::

    from pyipay import Gateway

    resource_file = r'/path/to/resource/resource.cgn'
    keystore_file = r'/path/to/keystore/keystore.bin'
    alias = 'SampleTerminal'
    redirect_url = 'https://knet-debugger.herokuapp.com'
    error_url = 'https://knet-debugger.herokuapp.com'

    # Generate an instance of the gateway

    gw = Gateway(resource_file, keystore_file, alias, 1.234)
    gw.response_url = redirect_url
    gw.error_url = error_url
    url = gw.generate_purchase_request()

`generate_purchase_request()` will return a URL, which you need to redirect the customer to. The gateway will
then respond to your redirect and error URLs.

The response needs to be decoded::

    result = gw.get_result(response_body)

Now `result` will be a dictionary with the following values:

+--------------+--------------+-----------------------------------------------------------------------------------------+
| Key          | Type         | Notes                                                                                   |
+==============+==============+=========================================================================================+
| paymentid    | Numeric      | A numeric payment id                                                                    |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| result       | Alpha        | The result, ie. "CAPTURED"                                                              |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| auth         | Alphanumeric | The authorization code                                                                  |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| amt          | Numeric      | The amount of the transaction                                                           |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| ref          | Alphanumeric | The transaction reference                                                               |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| postdate     | Numeric      | MMDD, the date the transaction is posted. It may be blank if the transaction is pending.|
+--------------+--------------+-----------------------------------------------------------------------------------------+
| trackid      | Numeric      | Merchant's trackid                                                                      |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| tranid       | Numeric      | A reference from the payment gateway for this transaction. Required for refunds, etc.   |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| avr          | Alphanumeric | The address verification response                                                       |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| authRespCode | Alphanumeric | The reason code for the transaction. Used for validation.                               |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| Error        | Numeric      | A numeric error code (optional)                                                         |
+--------------+--------------+-----------------------------------------------------------------------------------------+
| ErrorText    | Alphanumeric | A text representation of the error (optional)                                           |
+--------------+--------------+-----------------------------------------------------------------------------------------+

It is **crucial** that you save the above values, as this serves as an official record of the transaction; in addition
for inquiry or refund transaction you need values from the initial transaction.



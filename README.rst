=================================
FSS iPay Integration Kit (Python)
=================================

.. image:: https://img.shields.io/pypi/v/pyipay.svg
        :target: https://pypi.python.org/pypi/fsspyipay

.. image:: https://readthedocs.org/projects/pyipay/badge/?version=latest
        :target: https://pyipay.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/burhan/pyipay/shield.svg
     :target: https://pyup.io/repos/github/burhan/pyipay/
     :alt: Updates


==========
DISCLAIMER
==========

**This is an unofficial port and is not supported by FSS. Use at your own risk.**

The package name is `fsspyipay` to avoid conflicts.

Welcome
-------

An interface for the FSS iPay terminal integration. This is the successor to the e24PaymentPipe kit which is used in Kuwait by KNET.

* Free software: MIT license
* Documentation: https://pyipay.readthedocs.io.

Requirements
------------
* Python 3. Python 2 is **not supported**.
* You must already have the integration kit. The kit includes `resource.cgn`, `keystore.bin` and the alias.

Notes
-----
In this initial release, only the payment functionality is available.

The following features are planned for subsequent releases:

* refunds and inquiry
* compatibility with the raw interface
* hosted transactions

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

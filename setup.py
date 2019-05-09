#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pyDes', 'pyjks', 'iso4217']

setup(
    author="Burhan Khalid",
    author_email='burhan.khalid@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="An interface for the FSS iPay terminal integration. This is the successor to the e24PaymentPipe kit which is used in Kuwait by KNET.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='knet, payments, kuwait, fss',
    name='fsspyipay',
    packages=find_packages(include=['pyipay']),
    url='https://github.com/burhan/pyipay',
    version='0.1.0',
    zip_safe=False,
)

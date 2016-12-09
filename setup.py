# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup


setup(
    name='restfm',
    version='0.0.1.dev0',
    description="Python client library for RESTfm",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ],
    keywords='Python Filemaker RestFM',
    author='René Jochum',
    author_email='rene.jochum@mariaebene.at',
    url='http://pypi.python.org/pypi/restfm',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'aiohttp',
        'simplejson'
    ]
)

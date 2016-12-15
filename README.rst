python client library for `RESTfm`_
===================================

.. image:: https://travis-ci.org/mariaebene/py-restfmclient.svg?branch=master
    :target: https://travis-ci.org/mariaebene/py-restfmclient

.. image:: https://codecov.io/gh/mariaebene/py-restfmclient/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/mariaebene/py-restfmclient

**In short** This library gives you full access to Filemaker with a pythonic api.

RESTfm gives you full Create, Read, Update and Delete ( CRUD ) operations on FileMaker Server hosted data via standard HTTP GET, POST, PUT and DELETE methods, this means you can get can get access to Filemaker over HTTP and with this library of also with Python 3.5+.


Requirements
------------

- Python 3.5+
- Tested with FileMaker 15 Server, should work with others.


Available over pip
------------------

We upload releases to pypi, you can get restfmclient over pip::

   pip3 install restfmclient


Install RESTfm on \*nix
-----------------------

- Install Apache with mod_php or better nginx with php-fpm, there are a lot tutorials for that.
- Download RESTfm from https://github.com/GoyaPtyLtd/RESTfm/releases and extract it to /var/www::

   wget https://github.com/GoyaPtyLtd/RESTfm/releases/download/v4.0.8/RESTfm-4.0.8.tgz
   sudo tar xfz RESTfm-4.0.8.tgz -C /var/www

- Copy *FileMaker Server\Web Publishing\FM_API_for_PHP_Standalone.zip* on your server (use winscp or scp).
- Extract FM_API_for_PHP_Standalone.zip on the linux box::

   cd /var/www/RESTfm/FileMaker/
   unzip ~/FM_API_for_PHP_Standalone.zip

- Configure RESTfm::

   nano RESTfm.ini.php

- Adjust at least: $config['database']['hostspec']


Install RESTfm on Windows
-------------------------

- Same as with Linux but with `XAMPP`_, get the PHP 5.6 version.


Run the example
---------------

- Git clone::

   git clone https://github.com/mariaebene/py-restfmclient.git

- Install the FileMaker example DB on your host, copy examples/restfm_example.fmp12 on it and activate the db.

- virtualenv::

   cd py-restfmclient
   virtualenv -p /usr/bin/python3.5 --no-site-packages venv

- pip install::

   ./venv/bin/pip3 install -r requirements_dev.txt

- install restfmclient::

   ./venv/bin/python3 setup.py develop

- Run it::

   ./venv/bin/python3 examples/restfm_client.py "http://<ip-or-dnsname-of-restfm-box>/RESTfm/" admin supersecretpw

- Or run with the RESTfm demo server::

   ./venv/bin/python3 examples/restfm_client.py "http://demo.restfm.com/RESTfm/" write restfm


Install in your own project
---------------------------

Its recommended to use a virtualenv for your project.

Install via pip::

   pip3 install restfmclient

aiohttp works a lot better with cchardet, aiodns and uvloop so install those::

   pip3 install cchardet aiodns uvloop

Activate uvloop in your own scripts::

   import uvloop
   asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


Testing
-------

Just install *requirements_dev.txt* and run **nosetests** for a simple mocked test::

    git clone https://github.com/mariaebene/py-restfmclient.git
    cd py-restfmclient
    virtualenv -p /usr/bin/python3.5 --no-site-packages venv
    source venv/bin/activate
    pip3 install -r requirements_dev.txt
    nosetests

If you want to run the tests against a live server you have to install *examples/restfm_example.fmp12* on the Filemaker server, then you can run it by giving the ENV variable **RESTFM_BASE_URL**::

    RESTFM_BASE_URL='http://admin:supersecretpw@<<ip-or-dnsname-of-restfm-box>/RESTfm/' nosetests


Development
-----------

Please provide pull requests if you want to improve py-restfmclient, just make sure that you don't break the API if not required.
Please run nosetests before you create a PR if you can.

To update the test mock files, run::

    rm -rf restfmclient/tests/data/*
    RESTFM_BASE_URL='http://admin:supersecretpw@<<ip-or-dnsname-of-restfm-box>/RESTfm/' RESTFM_STORE_PATH='restfmclient/tests/data/' nosetests

We use `zest.releaser`_ to create a release and upload it to pypi.


LICENSE
-------

Copyright 2017 - Stiftung Maria Ebene, licensed under the MIT license.

.. _`RESTfm`: http://restfm.com/
.. _`XAMPP`: https://www.apachefriends.org/de/download.html
.. _`zest.releaser`: https://pypi.python.org/pypi/zest.releaser
.. _`Semantic Versioning`: http://semver.org/

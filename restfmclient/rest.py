# -*- coding: utf-8 -*-
from collections import OrderedDict
from os import path
from urllib.parse import unquote
from urllib.parse import urlencode

import aiohttp
import copy
import os
import urllib.parse as urlparse


try:
    import simplejson as json
except ImportError:
    import json

try:
    import aiofiles
    HAS_AIOFILES = True
except ImportError:  # pragma: no cover
    HAS_AIOFILES = False


class RestNotFoundException(Exception):
    pass


class RestDecoderException(Exception):
    def __init__(self, result):
        self._result = result
        super(RestDecoderException, self).__init__(
            "Failed to decode the result"
        )

    @property
    def result(self):
        return self._result


class Rest(object):

    def __init__(self, loop, logger):
        self._loop = loop
        self._logger = logger

        # Parameters
        self._verify_ssl = True
        self._session = None
        self._timeout = 360
        self._headers = {
            'Content-Type': 'application/json'
        }

        self._base_url = ''
        self._path = ''
        self._query = {}

    def clone(self):  # pragma: no cover
        clone = Rest(self._loop, self._logger)
        clone.verify_ssl = self.verify_ssl
        clone.session = self.session
        clone.timeout = self.timeout
        clone.headers = copy.copy(self.headers)
        clone.base_url = self.base_url
        clone.path = self.path

        return clone

    # Parameters
    @property
    def logger(self):
        return self._logger

    # Parameters
    @logger.setter
    def logger(self, value):
        self._logger = value

    # Parameters
    @property
    def loop(self):
        return self._loop

    @property
    def verify_ssl(self):
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, value):
        self._verify_ssl = value

    @property
    def session(self):
        if self._session is None:
            conn = aiohttp.TCPConnector(
                loop=self._loop, verify_ssl=self.verify_ssl
            )
            self._session = aiohttp.ClientSession(
                loop=self._loop, connector=conn
            )

        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    # URL manipulation
    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    # Header manipulation
    def set_header(self, key, value):
        self._headers[key] = value

    def get_header(self, key):
        return self._headers[key]

    def basic_auth(self, username, password):
        self.set_header(  # pragma: no cover
            'Authorization',
            aiohttp.BasicAuth(username, password).encode()
        )

    # HTTP Methods
    async def get(self, store_path=None):
        return await self._request('get', store_path=store_path)

    async def post(self, data, store_path=None):
        return await self._request(
            'post', store_path=store_path, data=json.dumps(data)
        )

    async def put(self, data, store_path=None):
        return await self._request(
            'put', store_path=store_path, data=json.dumps(data)
        )

    async def delete(self, store_path=None):
        return await self._request('delete', store_path=store_path)

    def url(self):
        url_parts = list(urlparse.urlparse(self._base_url + self._path))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(self._query)
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    async def _store(self, store_path, method, url, result):
        if not HAS_AIOFILES:  # pragma: no cover
            return

        url_parts = list(urlparse.urlparse(url))
        filename = 'index.json'
        if url_parts[4] != '':
            query = OrderedDict(
                sorted(dict(urlparse.parse_qsl(url_parts[4])).items())
            )
            filename += '?%s' % urlencode(query)
        save_path = path.join(
            unquote(path.join(
                store_path,
                url_parts[2][1:],
                method.lower(),
            )),
            filename
        )

        try:
            os.makedirs(path.dirname(save_path), 0o755)
        except OSError:  # pragma: no cover
            # Dir exists.
            pass

        self.logger.debug('Saving: %s, len: %d' % (save_path, len(result)))
        async with aiofiles.open(save_path, mode='w', loop=self._loop) as f:
            await f.write(result)

    async def _request(self, method, store_path=None, **kwargs):
        with aiohttp.Timeout(self.timeout, loop=self.session.loop):
            url = self.url()
            self.logger.debug('HTTP %s %s' % (method.upper(), url))
            kwargs['headers'] = self.headers
            async with self.session.request(method, url, **kwargs) as response:
                if self.headers['Content-Type'] == 'application/json':
                    result = await response.text()
                    if store_path is not None:
                        await self._store(store_path, method, url, result)

                    if response.status == 404:  # pragma: no cover
                        raise RestNotFoundException("Not found.")

                    try:
                        return json.loads(result)
                    except json.decoder.JSONDecodeError:
                        raise RestDecoderException(result)

                else:  # pragma: no cover
                    return await response.text()

    async def close(self):
        if self._session is not None:
            await self._session.close()
            self._session = None

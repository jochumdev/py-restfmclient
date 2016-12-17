# -*- coding: utf-8 -*-
from copy import copy
from pytz import timezone
from restfmclient.database import Database
from restfmclient.exceptions import RESTfmException
from restfmclient.exceptions import RESTfmNotFound
from restfmclient.rest import Rest
from restfmclient.rest import RestDecoderException
from restfmclient.rest import RestNotFoundException
from restfmclient.version import __version__
from tzlocal import get_localzone

import logging


mylogger = logging.getLogger('RESTfmClient')


class RESTfm(Rest):

    def __init__(self, loop, logger):
        super(RESTfm, self).__init__(loop, logger)

        self.set_header('User-Agent', 'py-restfm/' + __version__)
        self._store_path = None
        self._timezone = None

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value

    @property
    def store_path(self):
        return self._store_path

    @store_path.setter
    def store_path(self, value):
        self._store_path = value

    def clone(self):
        clone = RESTfm(self._loop, self._logger)
        clone.store_path = self.store_path
        clone.verify_ssl = self.verify_ssl
        clone.session = self.session
        clone.timeout = self.timeout
        clone.headers = copy(self.headers)
        clone.base_url = self.base_url
        clone.path = self.path

        clone.timezone = self.timezone

        return clone

    async def _fm_request(self, method, data=None):
        result = ''
        try:
            func = getattr(super(RESTfm, self), method)
            if data is None:
                result = await func(store_path=self._store_path)
            else:
                result = await func(data, store_path=self._store_path)

        except RestDecoderException as e:
            raise RESTfmException(self.url(), data, e)

        except RestNotFoundException as e:  # pragma: no cover
            raise RESTfmNotFound("Record not found") from e  # pragma: no cover

        statuscode = result['info']['X-RESTfm-Status']
        if 'X-RESTfm-FM-Status' in result['info']:
            statuscode = int(result['info']['X-RESTfm-FM-Status'])
        if (statuscode == 404 or statuscode == 401 or
                statuscode == 105 or statuscode == 101):
            raise RESTfmNotFound("Record not found")

        if (statuscode > 299 or statuscode < 200):
            raise RESTfmException(self.url(), data, result)

        return result

    async def get(self):
        return await self._fm_request('get')

    async def put(self, data):
        return await self._fm_request('put', data)

    async def post(self, data):
        return await self._fm_request('post', data)

    async def delete(self):
        return await self._fm_request('delete')


class Client(object):

    def __init__(self, loop, base_url,
                 username=None, password=None, verify_ssl=True,
                 tz=None, logger=None):
        if logger is None:
            logger = mylogger
        self._client = RESTfm(loop, logger)
        self._client.verify_ssl = verify_ssl
        self._client.base_url = base_url

        if isinstance(tz, (str,)):
            self._client.timezone = timezone(tz)
        elif tz is None:
            self._client.timezone = get_localzone()

        else:
            self._client.timezone = tz

        if username is not None and password is not None:
            self._client.basic_auth(username, password)  # pragma: no cover

    @property
    def rest_client(self):
        return self._client

    @property
    def store_path(self):
        return self._client.store_path

    @store_path.setter
    def store_path(self, value):
        self._client.store_path = value

    async def list_dbs(self):
        if self._client is None:
            return []  # pragma: no cover

        client = self._client.clone()
        client.path = '.json'
        client.query = {'RFMlink': 'layout'}
        json = await client.get()

        result = []
        for v in json['data']:
            result.append(v['database'])

        return result

    def get_db(self, name):
        if self._client is None:
            return None  # pragma: no cover

        return Database(self._client.clone(), name)

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()  # pragma: no cover

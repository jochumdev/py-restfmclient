# -*- coding: utf-8 -*-
from restfmclient.cursor import Cursor
from restfmclient.exceptions import RESTfmNotFound
from restfmclient.record import info_from_resultset
from restfmclient.record import Record
from urllib.parse import quote


class Layout(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

        self._field_info = None

        self._client.path += 'layout/' + quote(self._name) + '/'

        self._count = None

    @property
    def name(self):
        return self._name

    @property
    def client(self):
        return self._client.clone()

    @property
    async def count(self):
        try:
            await self.get_one()
        except RESTfmNotFound:
            return 0

        return self._count

    @property
    async def field_info(self):
        if self._field_info is not None:
            return self._field_info

        client = self.client
        client.path += '.json'
        client.query['RFMmetaFieldOnly'] = '1'

        result = await client.get()

        if self._field_info is None or self._count is None:
            field_info, count = info_from_resultset(result)
            if self._field_info is None:
                self._field_info = field_info
            if self._count is None:
                self._count = count

        return self._field_info

    @field_info.setter
    def field_info(self, value):
        self._field_info = value

    def get(self, search=None, sql=None, block_size=100,
            limit=None, offset=0, prefetch=True):
        client = self.client
        client.path += '.json'
        if sql is not None:
            client.query['RFMfind'] = sql

        searchNum = 1
        if search is not None:
            for k, v in search.items():
                client.query['RFMsF%d' % searchNum] = k
                client.query['RFMsV%d' % searchNum] = v
                searchNum += 1

        return Cursor(
            client,
            block_size=block_size,
            limit=limit, offset=offset,
            field_info=self._field_info
        )

    async def get_one(self, search=None, sql=None, skip=0):
        client = self.client
        client.path += '.json'
        if sql is not None:
            client.query['RFMfind'] = sql

        searchNum = 1
        if search is not None:
            for k, v in search.items():
                client.query['RFMsF%d' % searchNum] = k
                client.query['RFMsV%d' % searchNum] = v
                searchNum += 1

        client.query['RFMmax'] = 1
        if skip != 0:
            client.query['RFMskip'] = skip

        result = await client.get()

        if self._field_info is None or self._count is None:
            field_info, count = info_from_resultset(result)
            if self._field_info is None:
                self._field_info = field_info
            if self._count is None:
                self._count = count

        if 'data' not in result:
            raise RESTfmNotFound()

        return Record(self.client, self._field_info,
                      result['data'][0], result['meta'][0]['recordID'])

    async def get_by_id(self, id):
        client = self.client

        client.path += str(id) + '/.json'
        result = await client.get()

        if self._field_info is None:
            self._field_info, self._count = info_from_resultset(result)

        return Record(self.client, self._field_info,
                      result['data'][0], id)

    async def create(self):
        return Record(self.client, await self.field_info)

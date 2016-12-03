# -*- coding: utf-8 -*-
from restfmclient.record import Record
from restfmclient.record import info_from_resultset
from restfmclient.record_iterator import RecordIterator
from urllib.parse import quote


class Layout(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

        self._field_info = None

        self._client.path += 'layout/' + quote(self._name) + '/'

        self._count = None

    @property
    async def count(self):
        if self._count is not None:
            return self._count

        await self.get_one()
        return self._count

    @property
    async def field_info(self):
        if self._field_info is not None:
            return self._field_info

        await self.get(1)
        return self._field_info

    def get(self, sql=None, block_size=100,
            limit=None, offset=0, prefetch=True):
        client = self._client.clone()
        client.path += '.json'
        if sql is not None:
            client.query['RFMfind'] = sql

        return RecordIterator(client, block_size=block_size,
                              limit=limit, offset=offset)

    async def get_one(self, sql=None, skip=0):
        client = self._client.clone()
        client.path += '.json'
        if sql is not None:
            client.query['RFMfind'] = sql
        client.query['RFMmax'] = 1
        if skip != 0:
            client.query['RFMskip'] = skip

        result = await client.get()
        if self._field_info is None:
            self._field_info, self._count = info_from_resultset(result)

        return Record(self._client, self._field_info,
                      result['data'][0], result['meta'][0]['recordID'])

    async def get_by_id(self, id):
        client = self._client.clone()

        client.path += str(id) + '/.json'
        result = await client.get()

        if self._field_info is None:
            self._info_from_resultset(result)

        return Record(self._client, self._field_info,
                      result['data'][0], id)

    async def create(self):
        return Record(self._client, await self.field_info)

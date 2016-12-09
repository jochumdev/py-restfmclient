# -*- coding: utf-8 -*-
from restfmclient.layout import Layout
from restfmclient.script import Script
from restfmclient.util import TimzoneManager


class Database(TimzoneManager):

    def __init__(self, client, name):
        super(Database, self).__init__(client)
        self._client = client
        self._name = name

        self._client.path += self._name + '/'
        self._timezone = self._client.timezone

    @property
    def name(self):
        return self._name

    async def list_layouts(self):
        client = self._client.clone()
        client.timezone = self._timezone

        client.path += 'layout.json'
        json = await client.get()

        result = []
        if 'data' not in json:
            return result  # pragma: no cover

        for v in json['data']:
            result.append(v['layout'])

        return result

    def layout(self, name):
        client = self._client.clone()
        client.timezone = self._timezone

        return Layout(client, name)

    async def list_scripts(self):
        client = self._client.clone()
        client.timezone = self._timezone

        client.path += 'script.json'
        json = await client.get()

        result = []
        if 'data' not in json:
            return result  # pragma: no cover

        for v in json['data']:
            result.append(v['script'])

        return result

    def script(self, name):
        client = self._client.clone()
        client.timezone = self._timezone

        return Script(client, name)

# -*- coding: utf-8 -*-

from restfmclient.layout import Layout
from restfmclient.script import Script


class Database(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

        self._client.path += self._name + '/'

    @property
    def name(self):
        return self._name

    async def list_layouts(self):
        client = self._client.clone()

        client.path += 'layout.json'
        json = await client.get()

        result = []
        if 'data' not in json:
            return result

        for v in json['data']:
            result.append(v['layout'])

        return result

    def layout(self, name):
        return Layout(self._client.clone(), name)

    async def list_scripts(self):
        client = self._client.clone()

        client.path += 'script.json'
        json = await client.get()

        result = []
        if 'data' not in json:
            return result

        for v in json['data']:
            result.append(v['script'])

        return result

    def script(self, name):
        return Script(self._client.clone(), name)

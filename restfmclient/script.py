# -*- coding: utf-8 -*-
from restfmclient.record_iterator import RecordIterator
from urllib.parse import quote


class Script(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name
        self._client.path += 'script/' + quote(self._name) + '/'

    def execute(self, layout, scriptParam=None, limit=None):
        client = self._client.clone()
        client.path += quote(layout) + '/.json'
        if scriptParam is not None:
            client.query['RFMscriptParam'] = scriptParam

        return RecordIterator(client, block_size=None, limit=limit)

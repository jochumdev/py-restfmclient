# -*- coding: utf-8 -*-
from restfmclient.cursor import Cursor
from restfmclient.util import TimzoneManager
from urllib.parse import quote


class Script(TimzoneManager):

    def __init__(self, client, name):
        super(Script, self).__init__(client)
        self._client = client
        self._name = name
        self._client.path += 'script/' + quote(self._name) + '/'

        self._field_info = None

    @property
    def field_info(self):
        return self._field_info

    @field_info.setter
    def field_info(self, value):
        self._field_info = value

    def execute(self, layout, scriptParam=None, limit=None):
        client = self._client.clone()
        client.timezone = self._timezone

        client.path += quote(layout) + '/.json'
        if scriptParam is not None:
            client.query['RFMscriptParam'] = scriptParam

        return Cursor(
            client, block_size=None, limit=limit,
            field_info=self._field_info
        )

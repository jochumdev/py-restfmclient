# -*- coding: utf-8 -*-
from collections import Mapping

import restfmclient.types


def info_from_resultset(result):
    fields = {}
    for field in result['metaField']:
        if field['resultType'] == 'timestamp':
            converter = restfmclient.types.Timestamp
        else:
            converter = restfmclient.types.Text

        fields[field['name']] = {
            'auto_entered': field['autoEntered'],
            'global': field['global'],
            'max_repeat': field['maxRepeat'],
            'type': field['resultType'],
            'converter': converter
        }

    count = None
    if 'info' in result and 'foundSetCount' in result['info']:
        count = int(result['info']['foundSetCount'])

    return (fields, count,)


class Record(dict):

    def __init__(self, client, field_info, data={}, record_id=None):
        self._client = client
        self._field_info = field_info
        self._record_id = record_id

        self._modified = False
        self._modified_fields = {}

        self._deleted = False

        for k, v in data.items():
            field_info = self._field_info[k]

            if field_info['converter'] is not None:
                super(Record, self).__setitem__(
                    k, field_info['converter'].from_fm(v, self._client)
                )

    @property
    def record_id(self):
        return self._record_id

    @property
    def modified(self):
        return self._modified

    @property
    def modified_fields(self):
        return self._modified_fields

    async def save(self):
        if (self._deleted or
            (not self.modified and
             self.record_id is not None)):  # pragma: no cover
            return

        if self.record_id is None:
            # New
            client = self._client.clone()
            client.path += '.json'
            result = await client.post({'data': [self.modified_fields]})
            self._record_id = result['meta'][0]['recordID']
            return

        # Modified
        client = self._client.clone()
        client.path += "%s/.json" % self.record_id
        await client.put({'data': [self.modified_fields]})
        return

    async def delete(self):
        if self._deleted:  # pragma: no cover
            return

        client = self._client.clone()

        # Ugly hack to fix the URL for deletions when coming
        # from a Cursor.
        if client.path.endswith('.json'):
            client.path = client.path[0:-5]

        client.path += "%s/.json" % self.record_id
        await client.delete()
        self._deleted = True

    def __setitem__(self, key, value):
        # Raises KeyError on unknown field.
        field_info = self._field_info[key]

        if self.get(key, None) == value:
            return

        self._modified = True
        if field_info['converter'] is not None:
            self._modified_fields[key] = field_info['converter'].to_fm(
                value, self._client
            )
        else:
            self._modified_fields[key] = value

        super(Record, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def update(self, other=None, **kwargs):
        if other is not None:
            for k, v in other.items() if isinstance(other, Mapping) else other:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

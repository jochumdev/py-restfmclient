# -*- coding: utf-8 -*-


def info_from_resultset(result):
    fields = {}
    for field in result['metaField']:
        fields[field['name']] = {
            'auto_entered': field['autoEntered'],
            'global': field['global'],
            'max_repeat': field['maxRepeat'],
            'type': field['resultType']
        }

    count = None
    if 'info' in result and 'foundSetCount' in result['info']:
        count = int(result['info']['foundSetCount'])

    return (fields, count,)


class Record(dict):

    def __init__(self, client, field_info, data={}, record_id=None):
        self.update(**data)

        self._client = client
        self._field_info = field_info
        self._record_id = record_id

        self._modified = False
        self._modified_fields = []

        self._deleted = False

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
        if self._deleted or (not self.modified and self.record_id is not None):
            return

        if self.record_id is None:
            # New
            client = self._client.clone()
            client.path += '.json'
            result = await client.post({'data': [self]})
            self._record_id = result['meta'][0]['recordID']
            return

        # Modified
        client = self._client.clone()
        client.path += "%s/.json" % self.record_id
        update = {}
        for field in self._modified_fields:
            update[field] = self[field]

        await client.put({'data': [update]})
        return

    async def delete(self):
        if self._deleted:
            return

        client = self._client.clone()
        client.path += "%s/.json" % self.record_id
        await client.delete()
        self._deleted = True

    def __setitem__(self, key, value):
        if dict.__getitem__(self, key) == value:
            return

        if key not in self._field_info:
            raise KeyError("Unknown field: %s" % key)

        self._modified = True
        self._modified_fields.append(key)

        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        raise NotImplemented

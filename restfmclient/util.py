# -*- coding: utf-8 -*-


class TimzoneManager(object):
    def __init__(self, client):
        self._timezone = client.timezone

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        self._timezone = value

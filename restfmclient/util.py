# -*- coding: utf-8 -*-
from pytz import timezone


class TimzoneManager(object):
    def __init__(self, client):
        self._timezone = client.timezone

    @property
    def timezone(self):
        return self._timezone.zone

    @timezone.setter
    def timezone(self, value):
        self._timezone = timezone(value)

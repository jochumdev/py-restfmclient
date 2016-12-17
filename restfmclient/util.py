# -*- coding: utf-8 -*-
import pytz


class TimzoneManager(object):
    def __init__(self, client):
        self._timezone = client.timezone

    @property
    def timezone(self):
        return self._timezone.zone

    @timezone.setter
    def timezone(self, value):
        if isinstance(value, (str,)):
            self._timezone = pytz.timezone(value)
        else:
            self._timezone = value

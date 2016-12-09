# -*- coding: utf-8 -*-
from datetime import datetime

import abc


class TypeConverter(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def to_fm(self, value, client):
        pass

    @abc.abstractmethod
    def from_fm(self, value, client):
        pass


class Text(TypeConverter):
    def to_fm(self, value, client):
        if value is None:
            return ''

        return value

    def from_fm(self, value, client):
        if value == '':
            return None

        return value


class Timestamp(TypeConverter):
    def to_fm(self, value, client):
        if value is None:
            return ''

        return value.astimezone(client.timezone).strftime('%m/%d/%Y %H:%M:%S')

    def from_fm(self, value, client):
        if value == '':
            return None

        date = datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
        return client.timezone.localize(date, is_dst=None)

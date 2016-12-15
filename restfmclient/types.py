# -*- coding: utf-8 -*-
from datetime import datetime

import abc
import uuid


class TypeConverter(object, metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def to_fm(cls, value, client):
        pass

    @classmethod
    @abc.abstractmethod
    def from_fm(cls, value, client):
        pass


class Text(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return value

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        return value


class Timestamp(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return value.astimezone(client.timezone).strftime('%m/%d/%Y %H:%M:%S')

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        date = datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
        return client.timezone.localize(date, is_dst=None)


class UUID(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return str(value).upper()

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        return uuid.UUID(value)

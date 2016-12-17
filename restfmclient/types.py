# -*- coding: utf-8 -*-
from datetime import datetime

import abc
import pytz
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


class TEXT(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        return value

    @classmethod
    def from_fm(cls, value, client):
        return value


class DATETIME(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return value.astimezone(client.timezone).strftime('%m/%d/%Y %H:%M:%S')

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        date = client.timezone.localize(
            datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
        ).astimezone(tz=None)

        return date


class DATETIME_UTC(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return value.astimezone(pytz.utc).strftime('%m/%d/%Y %H:%M:%S')

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        return pytz.UTC.localize(
            datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
        ).astimezone(tz=None)


class TIMESTAMP_UTC(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return int(
            value.astimezone(tz=pytz.utc)
                 .replace(microsecond=0)
                 .timestamp(),
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = int(str(value), base=10)
        return datetime.utcfromtimestamp(timestamp)\
                       .replace(tzinfo=pytz.utc)\
                       .astimezone(tz=None)


class TIMESTAMP_UTC_FLOAT(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return float(
            value.astimezone(tz=pytz.utc)
                 .timestamp(),
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = float(value)
        return datetime.utcfromtimestamp(timestamp)\
                       .replace(tzinfo=pytz.utc)\
                       .astimezone(tz=None)


class TIMESTAMP(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return int(
            value.astimezone(tz=client.timezone).timestamp(),
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = int(str(value), base=10)
        return datetime.fromtimestamp(timestamp, tz=client.timezone)\
                       .replace(microsecond=0)\
                       .astimezone(tz=None)


class TIMESTAMP_FLOAT(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return float(
            value.astimezone(tz=pytz.utc)
                 .timestamp()
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = float(value)
        return datetime.fromtimestamp(timestamp, tz=client.timezone)\
                       .astimezone(tz=None)


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


class INTEGER(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        return value

    @classmethod
    def from_fm(cls, value, client):
        return int(value, base=10)

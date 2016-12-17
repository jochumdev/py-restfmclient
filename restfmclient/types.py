# -*- coding: utf-8 -*-
from datetime import timezone as dt_timezone
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

        date = datetime.strptime(value, '%m/%d/%Y %H:%M:%S')
        return client.timezone.localize(date, is_dst=None)


class DATETIME_UTC(TypeConverter):
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
        return client.timezone.localize(date, is_dst=None)\
                              .astimezone(dt_timezone.utc)


class TIMESTAMP_UTC(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return int(
            value.astimezone(tz=dt_timezone.utc)
                 .replace(microsecond=0)
                 .timestamp(),
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = int(str(value), base=10)
        return datetime.utcfromtimestamp(timestamp)\
                       .replace(tzinfo=dt_timezone.utc)\
                       .astimezone(client.timezone)


class TIMESTAMP_UTC_FLOAT(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return float(
            value.astimezone(tz=dt_timezone.utc)
                 .timestamp(),
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = float(value)
        return datetime.utcfromtimestamp(timestamp)\
                       .replace(tzinfo=dt_timezone.utc)\
                       .astimezone(client.timezone)


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
                       .astimezone(tz=client.timezone)


class TIMESTAMP_FLOAT(TypeConverter):
    @classmethod
    def to_fm(cls, value, client):
        if value is None:
            return ''

        return float(
            value.astimezone(tz=dt_timezone.utc)
                 .timestamp()
        )

    @classmethod
    def from_fm(cls, value, client):
        if value == '':
            return None

        timestamp = float(value)
        return datetime.fromtimestamp(timestamp, tz=client.timezone)\
                       .astimezone(tz=client.timezone)


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

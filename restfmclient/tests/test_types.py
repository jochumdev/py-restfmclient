# -*- coding: utf-8 -*-
from pytz import timezone as pytz_timezone
from restfmclient import types
from restfmclient.client import Client
from tzlocal import get_localzone

import dateutil.parser
import unittest
import uuid


class TestCase(unittest.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        # We use Yakutsk, Russia timezone to check if they convert right
        # with the local one
        self.other_timezone = pytz_timezone('Asia/Yakutsk')
        if get_localzone() == self.other_timezone:
            self.other_timezone = pytz_timezone('Europe/Vienna')

        self.client = Client(None, 'http://localhost').rest_client

        self.a_date = dateutil.parser\
                              .parse('1986-03-06 09:28:47.251665+01:00')\
                              .astimezone(self.other_timezone)

        self.a_uuid = uuid.uuid1()

    def test_text(self):
        # No TEXT->None converter
        self.assertEqual(types.TEXT.from_fm('', self.client), '')
        self.assertEqual(types.TEXT.to_fm('', self.client), '')

        wanted = 'Lorem'
        fm_value = types.TEXT.to_fm(wanted, self.client)

        self.assertEqual(
            types.TEXT.from_fm(fm_value, self.client),
            wanted)

    def test_datetime(self):
        # TEXT->None converter
        self.assertEqual(types.DATETIME.from_fm('', self.client), None)
        self.assertEqual(types.DATETIME.to_fm(None, self.client), '')

        wanted = self.a_date.replace(microsecond=0)
        fm_value = types.DATETIME.to_fm(wanted, self.client)

        self.assertEqual(
            types.DATETIME.from_fm(fm_value, self.client),
            wanted)

    def test_datetime_utc(self):
        # TEXT->None converter
        self.assertEqual(types.DATETIME_UTC.from_fm('', self.client), None)
        self.assertEqual(types.DATETIME_UTC.to_fm(None, self.client), '')

        wanted = self.a_date.replace(microsecond=0)
        fm_value = types.DATETIME_UTC.to_fm(wanted, self.client)

        self.assertEqual(
            types.DATETIME_UTC.from_fm(fm_value, self.client),
            wanted)

    def test_timestamp_utc(self):
        # TEXT->None converter
        self.assertEqual(types.TIMESTAMP_UTC.from_fm('', self.client), None)
        self.assertEqual(types.TIMESTAMP_UTC.to_fm(None, self.client), '')

        wanted = self.a_date.replace(microsecond=0)
        fm_value = types.TIMESTAMP_UTC.to_fm(wanted, self.client)

        self.assertEqual(
            types.TIMESTAMP_UTC.from_fm(fm_value, self.client),
            wanted)

    def test_timestamp_utc_float(self):
        # TEXT->None converter
        self.assertEqual(
            types.TIMESTAMP_UTC_FLOAT.from_fm('', self.client), None
        )
        self.assertEqual(
            types.TIMESTAMP_UTC_FLOAT.to_fm(None, self.client), ''
        )

        wanted = self.a_date
        fm_value = types.TIMESTAMP_UTC_FLOAT.to_fm(wanted, self.client)

        self.assertEqual(
            types.TIMESTAMP_UTC_FLOAT.from_fm(fm_value, self.client),
            wanted)

    def test_timestamp(self):
        # TEXT->None converter
        self.assertEqual(
            types.TIMESTAMP.from_fm('', self.client), None
        )
        self.assertEqual(
            types.TIMESTAMP.to_fm(None, self.client), ''
        )

        wanted = self.a_date.replace(microsecond=0)
        fm_value = types.TIMESTAMP.to_fm(wanted, self.client)

        self.assertEqual(
            types.TIMESTAMP.from_fm(fm_value, self.client)
                           .astimezone(self.other_timezone),
            wanted
        )

    def test_timestamp_float(self):
        # TEXT->None converter
        self.assertEqual(
            types.TIMESTAMP_FLOAT.from_fm('', self.client), None
        )
        self.assertEqual(
            types.TIMESTAMP_FLOAT.to_fm(None, self.client), ''
        )

        wanted = self.a_date
        fm_value = types.TIMESTAMP_FLOAT.to_fm(wanted, self.client)

        self.assertEqual(
            types.TIMESTAMP_FLOAT.from_fm(fm_value, self.client),
            wanted)

    def test_uuid(self):
        # TEXT->None converter
        self.assertEqual(
            types.UUID.from_fm('', self.client), None
        )
        self.assertEqual(
            types.UUID.to_fm(None, self.client), ''
        )

        wanted = self.a_uuid
        fm_value = types.UUID.to_fm(wanted, self.client)

        self.assertEqual(
            types.UUID.from_fm(fm_value, self.client),
            wanted)

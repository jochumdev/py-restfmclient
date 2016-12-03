# -*- coding: utf-8 -*-
from aiohttp.test_utils import unittest_run_loop
from restfmclient.tests import RESTfmTestCase


class RecordIteratorTestCase(RESTfmTestCase):

    @unittest_run_loop
    async def test_limit_100_offset_10(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            numbers = []
            async for record in layout.get(limit=100, offset=10):
                numbers.append(int(record.record_id))

            self.assertEqual(
                numbers[0], 11, 'First number must be 11 as we have offset=10'
            )
            self.assertEqual(
                numbers[len(numbers) - 1], 110,
                'Last number must be 110 we have limit=100, offset=10'
            )

# -*- coding: utf-8 -*-
from aiohttp.test_utils import unittest_run_loop
from restfmclient.tests import RESTfmTestCase


class CursorTestCase(RESTfmTestCase):

    @unittest_run_loop
    async def test_bad_blocksize(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            try:
                async for record in await layout.get(block_size=3):
                    print(record['number'])
            except ValueError:
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_limit_500_offset_10(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            numbers = []
            async for record in await layout.get(limit=500, offset=10):
                numbers.append(int(record['number']))

            self.assertEqual(
                11, numbers[0], 'First number must be 11 as we have offset=10'
            )
            self.assertEqual(
                510, numbers[len(numbers) - 1],
                'Last number must be 510 we have limit=500, offset=10'
            )

    @unittest_run_loop
    async def test_limit_500_offset_10_no_block_size(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            numbers = []
            async for record in await layout.get(
                    limit=500, offset=10, block_size=None):
                numbers.append(int(record['number']))

            self.assertEqual(
                11, numbers[0], 'First number must be 11 as we have offset=10'
            )
            self.assertEqual(
                510, numbers[len(numbers) - 1],
                'Last number must be 510 we have limit=500, offset=10'
            )

    @unittest_run_loop
    async def test_limit_100_offset_10_no_prefetch(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            numbers = []
            async for record in await layout.get(
                    limit=100, offset=10, prefetch=False):
                numbers.append(int(record['number']))

            self.assertEqual(
                numbers[0], 11, 'First number must be 11 as we have offset=10'
            )
            self.assertEqual(
                numbers[len(numbers) - 1], 110,
                'Last number must be 110 we have limit=100, offset=10'
            )

    @unittest_run_loop
    async def test_limit_500_offset_4600_no_prefetch(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')
            numbers = []
            async for record in await layout.get(
                    limit=500, offset=4600, prefetch=False):
                numbers.append(int(record['number']))

            self.assertEqual(
                numbers[0], 4601, 'First number must be 4601 as we have offset=4600'  # noqa
            )
            self.assertEqual(
                numbers[len(numbers) - 1], 5000,
                'Last number must be 5000 we have limit=500, offset=4600 but only 5000 records'  # noqa
            )

    @unittest_run_loop
    async def test_fetch_all(self):
        async with self.client:
            layout = self.client.get_db('restfm_example')\
                                .layout('iterate_test')

            numbers = []
            async for record in await layout.get():
                numbers.append(record['number'])

            self.assertEqual(
                len(numbers), await layout.count
            )

# -*- coding: utf-8 -*-
from collections.abc import AsyncIterator
from restfmclient.exceptions import RESTfmNotFound
from restfmclient.record import info_from_resultset
from restfmclient.record import Record

import asyncio


class Cursor(AsyncIterator):
    def __init__(self, client, block_size=100,
                 limit=None, offset=0, prefetch=True, field_info=None):
        self._client = client
        self._limit = limit
        self._block_size = block_size
        self._offset = offset
        self._prefetch = prefetch

        if self._block_size is None:
            self._prefetch = False

        if self._limit is not None:
            if self._block_size is None or self._limit < self._block_size:
                self._block_size = None
                self._prefetch = False
                client.query['RFMmax'] = self._limit
            else:
                client.query['RFMmax'] = self._block_size
        else:
            client.query['RFMmax'] = self._block_size

        if offset != 0:
            client.query['RFMskip'] = offset

        if self._prefetch:
            if self._block_size % 2 != 0:
                raise ValueError('Block size must be a power of two')

            self._block_size_div = int(block_size / 2)

        self._field_info = field_info
        self._count = None

        self._current_block = None
        self._current_block_size = 1
        self._current_pos = 0
        self._current_block_pos = 0
        self._prefetcher = None

    async def _fetch(self, offset=0):
        if offset != 0:
            self._client.query['RFMskip'] = offset

        try:
            result = await self._client.get()
        except RESTfmNotFound:
            raise StopAsyncIteration

        if self._field_info is None or self._count is None:
            field_info, count = info_from_resultset(result)
            if self._field_info is None:
                self._field_info = field_info
            if self._count is None:
                self._count = count

        if 'data' not in result or isinstance(result['data'][0], (list,)):
            raise StopAsyncIteration

        records = []
        for idx, row in enumerate(result['data']):
            records.append(
                Record(self._client, self._field_info,
                       row, result['meta'][idx]['recordID'])
            )

        count = len(records)
        if 'fetchCount' in result['info']:
            count = int(result['info']['fetchCount'])
        return (records, count,)

    async def __aiter__(self):
        self._current_block = None
        self._current_block_size = 1
        self._current_pos = 0
        self._current_block_pos = 0

        self._prefetcher = asyncio.ensure_future(
            self._fetch(
                self._offset
            ),
            loop=self._client.loop
        )

        return self

    async def __anext__(self):
        if self._current_block is None:
            self._current_block, self._current_block_size = \
                await self._prefetcher
            self._current_block_pos = 0
            self._prefetcher = None

        if (self._limit is not None and self._current_pos >= self._limit):
            # Enforce the limit
            raise StopAsyncIteration

        if self._block_size is None:
            # Only one block
            if (self._current_block_pos >= self._current_block_size):
                raise StopAsyncIteration

            row = self._current_block[self._current_block_pos]
            self._current_pos += 1
            self._current_block_pos += 1

            return row

        # Multiple blocks with/without prefetch
        if (self._prefetcher is None and
                self._current_block_pos >= self._current_block_size):
            raise StopAsyncIteration

        if self._current_block_pos >= self._current_block_size:
            self._current_block, self._current_block_size = \
                await self._prefetcher
            self._current_block_pos = 0
            self._prefetcher = None

            if self._current_block_size == 0:
                raise StopAsyncIteration

        row = self._current_block[self._current_block_pos]
        self._current_pos += 1
        self._current_block_pos += 1

        if self._prefetch:
            # Need to fetch next block?
            if self._current_block_pos == self._block_size_div:
                # Do we have more rows to fetch
                if (self._count >
                        self._current_pos + self._block_size_div):
                    # Do we reach a limit?
                    if (self._limit is None or
                            self._current_pos + self._block_size_div <
                            self._limit):

                        # Then prefetch next rows.
                        self._prefetcher = asyncio.ensure_future(
                            self._fetch(
                                self._offset +
                                self._current_pos +
                                self._block_size_div
                            ),
                            loop=self._client.loop
                        )

            # With this asyncio gets time to prefetch
            await asyncio.sleep(0, loop=self._client.loop)

        elif self._current_block_pos >= self._current_block_size:
            # Do we have more rows to fetch
            if (self._count is not None and
                    self._count > self._current_pos):
                # Do we reach a limit?
                if (self._limit is None or self._current_pos < self._limit):
                    # Prefetch off, blocksize on
                    self._prefetcher = asyncio.ensure_future(
                        self._fetch(
                            self._offset +
                            self._current_pos +
                            self._block_size_div
                        ),
                        loop=self._client.loop
                    )

        return row

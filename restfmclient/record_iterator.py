# -*- coding: utf-8 -*-
import asyncio
from collections.abc import AsyncIterator
from restfmclient.record import Record
from restfmclient.record import info_from_resultset


class RecordIterator(AsyncIterator):
    def __init__(self, client, block_size=100,
                 limit=None, offset=0, prefetch=True):
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

        if offset != 0:
            client.query['RFMskip'] = offset

        if self._prefetch:
            if self._block_size % 2 != 0:
                raise ValueError('Block size must be a power of two')

            self._block_size_div = int(block_size / 2)

        self._field_info = None
        self._count = None

        self._current_block = None
        self._current_block_size = 1
        self._current_pos = 0
        self._current_block_pos = 0
        self._prefetcher = None

    @property
    async def count(self):
        if self._count is not None:
            return self._count

        await self._fetch()
        return self._count

    async def _fetch(self, offset=0):
        if offset != 0:
            self._client.query['RFMskip'] = offset

        print('Fetch: %s' % self._client.url())

        result = await self._client.get()

        if self._field_info is None:
            self._field_info, self._count = info_from_resultset(result)

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

    def __aiter__(self):
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

        row = self._current_block[self._current_block_pos]
        self._current_pos += 1
        self._current_block_pos += 1

        if self._prefetch:
            # Need to fetch next block?
            if self._current_block_pos == self._block_size_div:
                # Do we have more rows to fetch
                if (self._offset + self._count >
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
            await asyncio.sleep(0)

        elif self._current_block_pos >= self._current_block_size:
            # Do we have more rows to fetch
            if (self._count is not None and
                    self._offset + self._count > self._current_pos):
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

# -*- coding: utf-8 -*-
import os
import asyncio
import gc
import restfmclient
from aiohttp.test_utils import TestServer
from pathlib import Path
import unittest
import uvloop
from restfmclient.tests.file_server import make_mock_app


class RESTfmTestClient(restfmclient.Client):

    def __init__(self, app, scheme='http', host='127.0.0.1'):
        self._server = None
        if 'RESTFM_BASE_URL' not in os.environ:
            self._server = TestServer(app, scheme=scheme, host=host)

        self._loop = app.loop

        self._closed = False

    def setup_client(self):
        if self._server:
            base_url = str(self._server.make_url('/RESTfm/'))
        else:
            base_url = os.environ['RESTFM_BASE_URL']

        super(RESTfmTestClient, self).__init__(
            self._loop, base_url, verify_ssl=False
        )

        if 'RESTFM_STORE_PATH' in os.environ:
            self.store_path = os.environ['RESTFM_STORE_PATH']

    async def start_server(self):
        if self._server is not None:
            await self._server.start_server()

    async def close(self):
        if not self._closed:
            await self._client.close()
            if self._server is not None:
                await self._server.close()
            self._closed = True

    def __enter__(self):
        if self._server is not None:
            self._loop.run_until_complete(self.start_server())
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._loop.run_until_complete(self.close())

    async def __aenter__(self):
        await self.start_server()
        self.setup_client()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()


class RESTfmTestCase(unittest.TestCase):

    def get_app(self, loop):
        """Override the get_app method to return your application.
        """
        # it's important to use the loop passed here.
        path = str(Path(__file__).parent.joinpath('data'))
        return make_mock_app(
            loop,
            path,
        )

    def setUp(self):
        self.loop = uvloop.new_event_loop()
        asyncio.set_event_loop(None)

        self.app = self.get_app(self.loop)
        self.client = RESTfmTestClient(self.app)
        self.loop.run_until_complete(self.client.start_server())

    def tearDown(self):
        self.loop.run_until_complete(self.client.close())

        closed = self.loop.is_closed()
        if not closed:
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()
            self.loop.close()
        gc.collect()
        asyncio.set_event_loop(None)

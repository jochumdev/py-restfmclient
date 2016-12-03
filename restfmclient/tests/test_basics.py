# -*- coding: utf-8 -*-
import time
from aiohttp.test_utils import unittest_run_loop
from restfmclient.tests import RESTfmTestCase
from restfmclient import RESTfmException
from restfmclient import RESTfmNotFound


class RecordIteratorTestCase(RESTfmTestCase):

    @unittest_run_loop
    async def test_list_dbs(self):
        async with self.client:
            dbs = await self.client.list_dbs()
            self.assertIn('restfm_example', dbs)

    @unittest_run_loop
    async def test_nonexistant_db_list_layouts(self):
        async with self.client:
            db = self.client.get_db('nonexistant')
            try:
                await db.list_layouts()
            except RESTfmException:
                pass

    @unittest_run_loop
    async def test_list_layouts(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layouts = await db.list_layouts()
            self.assertEqual(3, len(layouts))

            # This is needed for further iterate tests:
            self.assertIn('iterate_test', layouts)

            # This is needed for CRUD tests and script tests.
            self.assertIn('us500', layouts)

    @unittest_run_loop
    async def test_nonexistant_layout_operations(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('nonexistant')
            try:
                await layout.get_one()
            except RESTfmNotFound:
                pass

    @unittest_run_loop
    async def test_crud(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            record = None
            try:
                record = await layout.get_one()
            except RESTfmException as e:
                import json
                print(json.dumps(e.trace()))
                raise e

            # Update
            record['web'] = 'https://www.restfm-update-%d.org' % time.time()
            await record.save()

            # Create a row
            record = await layout.create()
            record.update({
                'first_name': 'Max',
                'last_name': 'Mustermanns',
                'email': 'max@mustermanns.at',
                'phone1': '+43 664 88 12 23 56',
                'web': 'https://mustermans.at',
                'company_name': 'Stiftung Maria Ebene',
                'address': 'Maria Ebene 17',
                'city': 'Frastanz',
                'zip': '6820',
                'country': 'Austria',
            })
            await record.save()

            # Delete the created row
            await record.delete()

    @unittest_run_loop
    async def test_sql_query(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            records = []
            sql = 'SELECT "zip", "web" WHERE zip LIKE \'70000..80000\''
            async for record in layout.get(sql=sql):
                records.append(record)

            self.assertEqual(24, len(records))

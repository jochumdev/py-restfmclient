# -*- coding: utf-8 -*-
from aiohttp.test_utils import unittest_run_loop
from pprint import pprint
from restfmclient import RESTfmException
from restfmclient import RESTfmNotFound
from restfmclient import types
from restfmclient.tests import RESTfmTestCase

import copy
import dateutil.parser
import time


class BasicTestCase(RESTfmTestCase):

    @unittest_run_loop
    async def test_list_dbs(self):
        async with self.client:
            self.client.rest_client.get_header('User-Agent')

            dbs = await self.client.list_dbs()
            self.assertIn('restfm_example', dbs)

        # Ops on closed client.
        await self.client.close()
        await self.client.close()  # Cover :)
        await self.client.list_dbs()
        self.client.get_db('restfm_example')

    @unittest_run_loop
    async def test_nonexistant_db_list_layouts(self):
        async with self.client:
            db = self.client.get_db('nonexistant')
            try:
                await db.list_layouts()
            except RESTfmException as e:
                pprint(e.trace())
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_list_layouts(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            self.assertEqual('restfm_example', db.name)
            layouts = await db.list_layouts()
            self.assertEqual(len(layouts), 5)

            # This is needed for further iterate tests:
            self.assertIn('iterate_test', layouts)

            # This is needed for CRUD tests and script tests.
            self.assertIn('us500', layouts)

    @unittest_run_loop
    async def test_bad_no_json(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            rest_client = layout.client
            rest_client.path += '.html'
            try:
                await rest_client.get()
            except RESTfmException as e:
                pprint(e.trace())
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_nonexistant_layout_operations(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('nonexistant')
            try:
                await layout.get_one()
            except RESTfmNotFound:
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_store(self):
        async with self.client:
            # Get for the default saver.
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            await layout.get_one()
            async for record in await layout.get():
                print(record.record_id)

            # Now with the /tmp saver.
            self.client.store_path = '/tmp'
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            await layout.get_one()
            async for record in await layout.get():
                print(record.record_id)

            # The if is here for codecov ...
            if self.client.store_path == '/tmp':
                self.client.store_path = None

    @unittest_run_loop
    async def test_layout_count(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            count = await layout.count
            count = await layout.count  # Twice for coverage
            self.assertEqual(count, 500)

    @unittest_run_loop
    async def test_layout_field_info(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            stored_field_info = {
                'address': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'city': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'company_name': {'auto_entered': 0,
                                  'global': 0,
                                  'max_repeat': 1,
                                  'type': 'text'},
                'country': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'email': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'first_name': {'auto_entered': 0,
                                'global': 0,
                                'max_repeat': 1,
                                'type': 'text'},
                'last_name': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'phone1': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'phone2': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'state': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'web': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'text'},  # noqa
                'zip': {'auto_entered': 0, 'global': 0, 'max_repeat': 1, 'type': 'number'}}  # noqa

            field_info = await layout.field_info
            no_converter = copy.deepcopy(field_info)
            for v in no_converter.values():
                del(v['converter'])

            self.assertEqual(no_converter, stored_field_info)

    @unittest_run_loop
    async def test_layout_get_one_sql(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            stored_record = {
                'web': 'http://www.fbsbusinessfinance.com', 'zip': '78204'
            }

            sql = 'SELECT "zip", "web" WHERE zip LIKE \'70000..80000\''
            record = await layout.get_one(sql=sql, skip=5)
            self.assertEqual(record, stored_record)

    @unittest_run_loop
    async def test_get_one_by_field(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            record = await layout.get_one(
                search={'phone2': '856-264-4130'}
            )

            self.assertEqual(record['phone2'], '856-264-4130')

    @unittest_run_loop
    async def test_layout_get_by_id_notfound(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            try:
                await layout.get_by_id(1)
            except RESTfmNotFound:
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_layout_get_by_id(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            stored_record = {
                'address': '6 Greenleaf Ave',
                'city': 'San Jose',
                'company_name': 'C 4 Network Inc',
                'country': 'Santa Clara',
                'email': 'vinouye@aol.com',
                'first_name': 'Veronika',
                'last_name': 'Inouye',
                'phone1': '408-540-1785',
                'phone2': '408-813-4592',
                'state': 'CA',
                'web': 'http://www.cnetworkinc.com',
                'zip': '95111'
            }

            record = await layout.get_by_id(2471)
            self.assertEqual(record, stored_record)

    @unittest_run_loop
    async def test_layout_find_one(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            stored_row = {
                'address': '6 Greenleaf Ave',
                'city': 'San Jose',
                'company_name': 'C 4 Network Inc',
                'country': 'Santa Clara',
                'email': 'vinouye@aol.com',
                'first_name': 'Veronika',
                'last_name': 'Inouye',
                'phone1': '408-540-1785',
                'phone2': '408-813-4592',
                'state': 'CA',
                'web': 'http://www.cnetworkinc.com',
                'zip': '95111'
            }

            # https://github.com/GoyaPtyLtd/RESTfm/issues/12
            row = await layout.get_one(
                search={'email': 'vinouye*'},
            )

            self.assertEqual(row, stored_row)

    @unittest_run_loop
    async def test_update_unknown_field(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            record = await layout.get_one()

            try:
                record['unknown'] = 'I raise a KeyError'
            except KeyError:
                pass

            try:
                record['unknown2'] = 'I raise a KeyError'
            except KeyError:
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_del_field(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            record = await layout.get_one()

            try:
                del record['web']
            except NotImplementedError:
                pass

            try:
                del record['first_name']
            except NotImplementedError:
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_crud(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # Read
            record = await layout.get_one()

            record['web'] = record['web']  # For coverage

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

            check_record = await layout.get_by_id(record.record_id)
            self.assertEqual(check_record['web'], 'https://mustermans.at')

            # Delete the created row
            await record.delete()

    @unittest_run_loop
    async def test_bad_sql_query(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            # SETECT instead of SELECT here
            sql = 'SETECT "zip", "web" WHERE zip LIKE \'70000..80000\''
            try:
                await layout.get_one(sql=sql)
            except RESTfmException as e:
                pprint(e.trace())
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_sql_query(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            records_num = 0
            sql = 'SELECT "zip", "web" WHERE zip LIKE \'70000..80000\''
            async for record in await layout.get(sql=sql):
                records_num += 1
                self.assertGreaterEqual(int(record['zip']), 70000)
                self.assertLessEqual(int(record['zip']), 80000)

            self.assertEqual(records_num, 43)

    @unittest_run_loop
    async def test_sql_query_no_result(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('us500')

            records_num = 0
            sql = 'SELECT "zip", "web" WHERE state = "nonexistant"'
            async for record in await layout.get(sql=sql):
                records_num += 1
                print(record.record_id)

            self.assertEqual(records_num, 0)

    @unittest_run_loop
    async def test_list_scripts(self):
        async with self.client:
            db = self.client.get_db('restfm_example')

            scripts = await db.list_scripts()
            self.assertEqual(
                len(scripts), 1, 'More than one script found.'
            )

            # Needed for futher tests
            self.assertIn(
                'Find State',
                scripts,
                'Script "Find State" not found.'
            )

    @unittest_run_loop
    async def test_execute_script(self):
        async with self.client:
            db = self.client.get_db('restfm_example')

            script = db.script('Find State')

            records_num = 0
            async for record in script.execute(
                    layout='us500', scriptParam='LA'):
                records_num += 1
                self.assertEqual(record['state'], 'LA')

            self.assertEqual(records_num, 9)

    @unittest_run_loop
    async def test_execute_script_error(self):
        async with self.client:
            db = self.client.get_db('restfm_example')

            script = db.script('Find State')

            try:
                async for record in script.execute(layout='us500'):
                    print(record.record_id)
            except RESTfmException as e:
                pprint(e.trace())
                return

            raise Exception('Should never reach here.')

    @unittest_run_loop
    async def test_execute_script_limit(self):
        async with self.client:
            db = self.client.get_db('restfm_example')

            script = db.script('Find State')

            records_num = 0
            async for record in script.execute(
                    layout='us500', scriptParam='LA', limit=2):
                records_num += 1
                self.assertEqual(record['state'], 'LA')

            self.assertEqual(records_num, 2)

    @unittest_run_loop
    async def test_find_pk_0(self):
        async with self.client:
            db = self.client.get_db('restfm_example')
            layout = db.layout('testview1')

            async for row in await layout.get():
                await row.delete()

            field_info = await layout.field_info
            field_info['pk']['converter'] = types.INTEGER

            a_date = dateutil.parser\
                             .parse('1986-03-06 09:28:47.251665+01:00')\
                             .astimezone(layout.client.timezone)\
                             .replace(microsecond=0)

            wanted = {
                'pk': 0,
                'text': 'bla bla',
                'updated_at': a_date,
            }

            row = await layout.create()
            row.update(wanted)
            await row.save()

            have = await layout.get_one(
                search={'pk': 0}
            )

            self.assertDictEqual(have, wanted)

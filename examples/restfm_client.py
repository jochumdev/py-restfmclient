#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import asyncio
import restfmclient
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def example_db_operations(db):
    layout = db.layout('us500')
    # Update a row
    row = await layout.get_one()
    row['web'] = 'https://www.restfm-update-example.org'
    await row.save()
    print("UPDATED record: %s" % row.record_id)

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
    print("Saved record:\t%s" % record.record_id)

    # Delete the created row
    await record.delete()
    print("Deleted record:\t%s" % record.record_id)
    print()

    sql = 'SELECT "web" WHERE zip LIKE \'70000..80000\''
    print('Result of SQL:\t%s' % sql)
    async for record in layout.get(sql=sql):
        print("%s: %s" % (
            record.record_id, json.dumps(record))
        )
    print()

    # Run a Script
    script = db.script('Find State')
    print('Result of script "Find State":')
    async for record in script.execute(
            layout='us500', scriptParam='LA', limit=1):
        print("%s: %s" % (record.record_id, json.dumps(record)))
    print()


async def demo_server_operations(db):
    layout = db.layout('full postcodes')
    sql = 'SELECT Locality, Pcode WHERE (Pcode > 3000 AND Locality LIKE \'*melb*\') OR (Pcode < 3000 AND Locality LIKE \'*syd*\') OMIT Comments LIKE \'*box*\' ORDER BY Pcode DESC'  # noqa
    print('Result of SQL:\t%s' % sql)
    async for record in layout.get(sql=sql, limit=10, offset=5):
        print("%s: %s" % (
            record.record_id, json.dumps(record))
        )
    print()

    # Run a Script
    script = db.script('SimpleSearch')
    print('Result of script "SimpleSearch":')
    async for record in script.execute(
            layout='brief postcodes', scriptParam='7300'):
        print("%s: %s" % (record.record_id, json.dumps(record)))


async def examine(loop, base_url, username, password, verify_ssl):
    print('Server:\t' + base_url)
    try:
        async with restfmclient.Client(
                loop, base_url,
                username, password, verify_ssl) as client:

            dbs = await client.list_dbs()
            print('Databases:\t' + json.dumps(dbs))

            for dbname in dbs:
                db = client.get_db(dbname)
                layouts = await db.list_layouts()
                print(db.name + ' layouts:\t' + json.dumps(layouts))

                for layoutname in layouts:
                    layout = db.layout(layoutname)

                    print("%s/%s count:\t%s" % (
                        db.name, layoutname, await layout.count)
                    )

                    row = await layout.get_one()
                    print("%s/%s row:\t%s" % (
                        db.name, layoutname, json.dumps(row))
                    )

                scripts = await db.list_scripts()
                print(db.name + ' scripts:\t' + json.dumps(scripts) + '\n')

                if dbname == 'restfm_example':
                    await example_db_operations(db)

                if dbname == 'postcodes':  # demo.restfm.com
                    await demo_server_operations(db)

    except (restfmclient.RESTfmException) as e:
        print(json.dumps(e.trace(), indent=4))


async def main(loop):
    args = sys.argv

    await examine(loop, args[1], args[2], args[3], False)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))

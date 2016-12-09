# -*- coding: utf-8 -*-
from aiohttp import web
from aiohttp.web_exceptions import HTTPForbidden
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_reqrep import Response
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlencode
from yarl import unquote

import aiofiles
import os.path


def restfm_mock_filehandler(loop, directory):
    try:
        directory = Path(directory)
        if str(directory).startswith('~'):
            directory = Path(os.path.expanduser(str(directory)))
        directory = directory.resolve()
        if not directory.is_dir():
            raise ValueError('Not a directory')
    except (FileNotFoundError, ValueError) as error:
        raise ValueError(
            "No directory exists at '{}'".format(directory)) from error

    async def handler(request):
        filename = unquote(request.match_info['tail'])
        try:

            filepath = directory.joinpath(filename)\
                                .joinpath(request.method.lower())
            if request.rel_url.query:
                query = urlencode(
                    OrderedDict(sorted(request.rel_url.query.items()))
                )
                filepath = filepath.joinpath('index.json?%s' % query)
            else:
                filepath = filepath.joinpath('index.json')
            filepath = filepath.resolve()

        except (ValueError, FileNotFoundError) as error:
            # relatively safe
            raise HTTPNotFound() from error
        except Exception as error:
            # perm error or other kind!
            request.app.logger.exception(error)
            raise HTTPNotFound() from error

        if filepath.is_dir():
            raise HTTPForbidden()
        elif filepath.is_file():
            async with aiofiles.open(str(filepath), mode='r', loop=loop) as f:
                ret = await f.read()
        else:
            raise HTTPNotFound

        return Response(text=ret)

    return handler


def make_mock_app(loop, directory):
    app = web.Application(loop=loop)
    handler = restfm_mock_filehandler(loop, directory)
    app.router.add_route('*', '/{tail:.*}', handler)

    return app

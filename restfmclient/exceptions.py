# -*- coding: utf-8 -*-
from restfmclient.rest import RestDecoderException


class RESTfmException(Exception):

    def __init__(self, url, data, result):
        self._url = url
        self._data = data
        self._result = result

        if isinstance(result, (Exception,)):
            super(RESTfmException, self).__init__(
                str(result)
            )
        else:
            super(RESTfmException, self).__init__(
                result['info']['X-RESTfm-Trace']
            )

    def trace(self):
        if isinstance(self._result, (RestDecoderException,)):
            return {
                'status_code': 500,
                'url': self._url,
                'request_data': self._data,
                'result': self._result.result,
                'message': str(self._result),
            }
        elif isinstance(self._result, (Exception,)):  # pragma: no cover
            return {
                'status_code': 500,
                'url': self._url,
                'request_data': self._data,
                'result': '',
                'message': str(self._result),
            }
        else:
            return {
                'status_code': self._result['info']['X-RESTfm-Status'],
                'url': self._url,
                'request_data': self._data,
                'result': self._result,
                'message': self._result['info']['X-RESTfm-Trace'],
            }


class RESTfmNotFound(Exception):
    pass

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
            if 'X-RESTfm-FM-Reason' in result['info']:
                super(RESTfmException, self).__init__(
                    result['info']['X-RESTfm-FM-Reason']
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
        elif isinstance(self._result, (Exception,)):
            return {
                'status_code': 500,
                'url': self._url,
                'request_data': self._data,
                'result': '',
                'message': str(self._result),
            }  # pragma: no cover
        else:
            statuscode = self._result['info']['X-RESTfm-Status']
            if 'X-RESTfm-FM-Status' in self._result['info']:
                statuscode = int(self._result['info']['X-RESTfm-FM-Status'])

            message = self._result['info']['X-RESTfm-Trace']
            if 'X-RESTfm-FM-Reason' in self._result['info']:
                message = self._result['info']['X-RESTfm-FM-Reason']

            return {
                'status_code': statuscode,
                'url': self._url,
                'request_data': self._data,
                'result': self._result,
                'message': message,
            }


class RESTfmNotFound(Exception):
    pass

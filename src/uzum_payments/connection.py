import asyncio
import json
import logging
from typing import Union

import aiohttp
import requests

from uzum_payments import exceptions
from uzum_payments.const import REQUEST_LOG


class Connection:
    def __init__(self, session: Union[aiohttp.ClientSession, requests.Session], headers: dict, logger: logging.Logger, is_async: bool):
        self.session = session
        self.headers = headers
        self.logger = logger
        self.REQUEST_LOG = REQUEST_LOG
        self.is_async = is_async

    def close(self):
        return self.session.close()

    def _raise_for_status(self, resp: Union[aiohttp.ClientResponse, requests.Response], text: str,
                          method: str = None) -> dict:
        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            raise json.JSONDecodeError

        error_code = data.get('errorCode')
        status_code = resp.status if isinstance(resp, aiohttp.ClientResponse) else resp.status_code

        self.logger.debug(self.REQUEST_LOG.format(method=method or resp.request_info.method, url=resp.url, text=text,
                                                  status=error_code))

        if not error_code and status_code == 200:  # Request was successful
            return data

        raise_error(data, error_code, status_code)

    def _request(self, url: str, data: dict = None, method: str = 'POST') -> dict:
        try:
            with self.session.request(url=url, method=method, headers=self.headers, json=data) as resp:
                return self._raise_for_status(resp, resp.text, method)
        except requests.Timeout:
            raise exceptions.NotResponding
        except requests.ConnectionError:
            raise exceptions.NetworkError

    async def _async_request(self, url: str, data: dict = None, method: str = 'POST') -> dict:
        try:
            async with self.session.request(url=url, method=method, headers=self.headers, json=data) as resp:
                return self._raise_for_status(resp, await resp.text(), method)
        except asyncio.TimeoutError:
            raise exceptions.NotResponding
        except aiohttp.ServerDisconnectedError:
            raise exceptions.NetworkError

    def _request_model(self, url: str, data: dict = None, method: str = 'POST'):
        if self.is_async:
            return self._async_request(url, data, method)

        return self._request(url, data)


def raise_error(data: dict, error_code: Union[int, None], status_code: int) -> None:
    if status_code == 400:
        raise exceptions.BadRequest(data, error_code)
    elif status_code == 401:
        raise exceptions.SignatureError(data, error_code)
    elif status_code == 403:
        raise exceptions.FingerprintError(data, error_code)
    elif status_code == 422:
        raise exceptions.ValidationError(data, error_code)
    elif status_code == 500:
        raise exceptions.InternalServerError(data, error_code)

    if error_code >= 5000:
        raise exceptions.InternalError(data, error_code)
    elif error_code >= 3000:
        raise exceptions.PaymentErrors(data, error_code)
    elif error_code >= 2000:
        raise exceptions.ValidationError(data, error_code)
    elif error_code >= 1000:
        raise exceptions.AuthenticationError(data, error_code)

    raise exceptions.UnexpectedError(data, error_code)
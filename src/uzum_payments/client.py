import logging
from typing import Optional, Any, Union

import aiohttp
import requests

from .connection import Connection
from .const import BASE_CHECKOUT_URL


class ApiClient(Connection):
    """Performs requests to the Uzum Checkout API"""
    def __init__(self,
                 signature: str,
                 terminal_id: str,
                 merchant_access_token: Optional[str] = None,
                 content_language: str = 'ru-RU',
                 fingerprint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = BASE_CHECKOUT_URL,
                 session: Union[aiohttp.ClientSession, requests.Session] = None,
                 is_async: bool = False, ) -> None:
        """
        :param signature: В каждый запрос от мерчанта в Uzum checkout необходимо добавить заголовок X-Signature.
                  Значением заголовка является подпись тела запроса. Для создания подписи используется ECDSA c хеш алгоритмом SHA256.
                  Мерчант на своей стороне генерирует private key и передает в Uzum checkout public key для проверки подписи.
                  При обработке запроса от мерчанта, Uzum checkout будет использовать полученный public key для проверки подписи запроса.
                  Если подпись окажется не валидной, Uzum checkout вернет ответ с errorCode=1000.
        :param terminal_id: Идентификатор терминала
        :param merchant_access_token: JWT-токен, полученный при аутентификации пользователя с помощью UzumID
        :param content_language: Уникальный ключ, который используется для аутентификации запросов.
        :param fingerprint: Заголовок выставляется по результату успешного прохождения mTLS.
        :param api_key: Уникальный ключ, который используется для аутентификации запросов.
        :param base_url: URL-адрес API
        :param session: Экземпляр сессии
        :param is_async: Асинхронное выполнение запросов
        """

        self.signature = signature
        self.terminal_id = terminal_id
        self.content_language = content_language
        self.headers = {
            'X-Signature': self.signature,
            'Content-Language': self.content_language,
            'X-Terminal-Id': self.terminal_id,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }

        if merchant_access_token:
            self.merchant_access_token = merchant_access_token
            self.headers.update({'X-Merchant-Access-Token': self.merchant_access_token})

        if fingerprint:
            self.fingerprint = fingerprint
            self.headers.update({'X-Fingerprint': self.fingerprint})

        if api_key:
            self.api_key = api_key
            self.headers.update({'X-API-Key': self.api_key})

        self.base_url = base_url
        if not self.base_url[-1] == '/':
            self.base_url += '/'

        self.session = session or (aiohttp.ClientSession() if is_async else requests.Session())
        self.is_async = is_async
        self.logger = logging.getLogger(__name__)

        Connection.__init__(self, self.session, self.headers, self.logger, self.is_async)

    @classmethod
    def Async(cls,
              signature: str,
              terminal_id: str,
              merchant_access_token: Optional[str] = None,
              content_language: str = 'ru-RU',
              fingerprint: Optional[str] = None,
              api_key: Optional[str] = None,
              base_url: Optional[str] = BASE_CHECKOUT_URL,
              session: Union[aiohttp.ClientSession, requests.Session] = None,):
        """
        Returns the client in async mode.
        :param signature: В каждый запрос от мерчанта в Uzum checkout необходимо добавить заголовок X-Signature.
                  Значением заголовка является подпись тела запроса. Для создания подписи используется ECDSA c хеш алгоритмом SHA256.
                  Мерчант на своей стороне генерирует private key и передает в Uzum checkout public key для проверки подписи.
                  При обработке запроса от мерчанта, Uzum checkout будет использовать полученный public key для проверки подписи запроса.
                  Если подпись окажется не валидной, Uzum checkout вернет ответ с errorCode=1000.
        :param terminal_id: Идентификатор терминала
        :param merchant_access_token: JWT-токен, полученный при аутентификации пользователя с помощью UzumID
        :param content_language: Уникальный ключ, который используется для аутентификации запросов.
        :param fingerprint: Заголовок выставляется по результату успешного прохождения mTLS.
        :param api_key: Уникальный ключ, который используется для аутентификации запросов.
        :param base_url: URL-адрес API
        :param session: Экземпляр сессии
        """
        return cls(signature=signature,
                   terminal_id=terminal_id,
                   merchant_access_token=merchant_access_token,
                   content_language=content_language,
                   fingerprint=fingerprint,
                   api_key=api_key,
                   base_url=base_url,
                   session=session,
                   is_async=True)

    def register(self,
                 amount: Optional[float],
                 client_id: str,
                 currency: int,
                 order_number: str,
                 payment_details: Optional[str] = None,
                 success_url: Optional[str] = None,
                 failure_url: Optional[str] = None,
                 view_type: str = 'REDIRECT',
                 payment_params: dict[str, Any] = None,
                 merchant_params: Optional[dict[dict[str, Any]]] = None,
                 session_timeout_secs: int = 600,
                 **kwargs) -> dict:
        """
        Запрос регистрации одностадийного/двухстадийного платежа.
        https://www.inplat-tech.ru/docs/checkout/#tag/payment/operation/register_payment_api_v1_payment_register_post

        :param amount: Сумма платежа (в тийинах, без комиссии)
        :param client_id: Идентификатор клиента в системе мерчанта. Используется для создания привязок и мапинга платежей между Uzum Checkout и системой мерчанта.
        :param currency: Валюта платежа. Необходимо указать по стандарту ISO 4217 код. Например: российский рубль - RUB - 643; а узбекский сум - UZS - 860.
        :param order_number: Идентификатор заказа на стороне мерчанта
        :param payment_details: Детали платежа
        :param success_url: URL для редиректа, если платеж пройдет успешно
        :param failure_url: URL для редиректа, если платеж завершится ошибкой
        :param view_type: Тип отображения платежной страницы
        :param payment_params: Дополнительные параметры платежа
        :param merchant_params: Дополнительные параметры мерчанта
        :param session_timeout_secs: Максимальная продолжительность сессии в секундах
        :param kwargs:
        """
        url = f"{self.base_url}payment/register"

        if payment_params is None:
            payment_params = {'payType': 'ONE_STEP'}

        data = {
            "amount": amount,
            "clientId": client_id,
            "currency": currency,
            "paymentDetails": payment_details,
            "orderNumber": order_number,
            "successUrl": success_url,
            "failureUrl": failure_url,
            "viewType": view_type,
            "merchantParams": merchant_params,
            "sessionTimeoutSecs": session_timeout_secs,
        }

        if payment_params is None:
            data.update({"paymentParams": {'payType': 'ONE_STEP'}})
        else:
            data.update({"paymentParams": payment_params})

        return self._request_model(url, data={**data, **kwargs})

    def merchant_pay(self, process_data: dict[dict[str, Any]], order_id: str) -> dict:
        """
        Этот метод используют мерчанты Server to Server. Это метод оплаты биндом.
        https://www.inplat-tech.ru/docs/checkout/#tag/payment/operation/merchant_pay_api_v1_payment_merchantPay_post

        :param process_data: Данные способа оплаты
        :param order_id: Идентификатор заказа
        """
        url = f"{self.base_url}payment/merchantPay"
        data = {
            'processData': process_data,
            'orderId': order_id,
        }

        return self._request_model(url, data=data)

    def get_order_status(self, order_id: str) -> dict:
        """
        Получение информации о статусе платежа.
        https://www.inplat-tech.ru/docs/checkout/#tag/payment/operation/get_order_status_api_v1_payment_getOrderStatus_post

        :param order_id: Идентификатор заказа
        """
        url = f"{self.base_url}payment/getOrderStatus"
        data = {
            'orderId': order_id,
        }

        return self._request_model(url, data=data)

    def get_operation_state(self, operation_id: str) -> dict:
        """
        Получение состояния операции
        https://www.inplat-tech.ru/docs/checkout/#tag/payment/operation/get_operation_state_api_v1_payment_getOperationState_post

        :param operation_id: Идентификатор операции на стороне чекаута
        """
        url = f"{self.base_url}payment/getOperationState"
        data = {
            'operationId': operation_id,
        }

        return self._post_model(url, data=data)

    def complete(self, order_id: str, amount: int) -> dict:
        """
        Подтверждение двухстадийного платежа
        https://www.inplat-tech.ru/docs/checkout/#tag/acquiring/operation/complete_api_v1_acquiring_complete_post

        :param order_id: Идентификатор заказа
        :param amount: Сумма для комплита в тийинах
        """
        url = f"{self.base_url}acquiring/complete"
        data = {
            'orderId': order_id,
            'amount': amount,
        }

        return self._request_model(url, data=data)

    def refund(self, order_id: str, amount: int) -> dict:
        """
        Полный или частичный возврат платежа. Использовать этот метод можно только после того, как транзакция перешла в статус "COMPLETED"".
        https://www.inplat-tech.ru/docs/checkout/#tag/acquiring/operation/refund_api_v1_acquiring_refund_post

        :param order_id: Идентификатор заказа
        :param amount: Сумма для комплита в тийинах
        """
        url = f"{self.base_url}acquiring/refund"
        data = {
            'orderId': order_id,
            'amount': amount,
        }

        return self._request_model(url, data=data)

    def reverse(self, order_id: str, amount: int) -> dict:
        """
        Метод используется для отмены оплаты заказа. Это метод для расхолдирования средств на счету.
        Отмену можно выполнить, когда платёж находится в статусе "AUTHORIZED".
        https://www.inplat-tech.ru/docs/checkout/#tag/acquiring/operation/reverse_api_v1_acquiring_reverse_post

        :param order_id: Идентификатор заказа
        :param amount: Сумма для комплита в тийинах
        """
        url = f"{self.base_url}acquiring/reverse"
        data = {
            'orderId': order_id,
            'amount': amount,
        }

        return self._request_model(url, data=data)

    def get_bindings(self, client_id: str) -> dict:
        """
        Метод получения списка привязок пользователя
        https://www.inplat-tech.ru/docs/checkout/#tag/acquiring/operation/get_bindings_api_v1_acquiring_getBindings_post

        :param client_id: Метод получения списка привязок пользователя
        """
        url = f"{self.base_url}acquiring/getBindings"
        data = {
            'clientId': client_id,
        }

        return self._request_model(url, data=data)

    def __repr__(self):
        return '<Uzum Payments Client async={}>'.format(self.is_async)

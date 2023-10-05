import logging
from typing import Optional, Union

import aiohttp
import requests

from uzum_payments.connection import Connection
from uzum_payments.const import BASE_RECEIPT_URL


class ReceiptApiClient(Connection):
    """Performs requests to the Uzum Receipt producer API"""

    def __init__(self,
                 ssl_client_fingerprint: str,
                 base_url: Optional[str] = BASE_RECEIPT_URL,
                 session: Union[aiohttp.ClientSession, requests.Session] = None,
                 is_async: bool = False, ) -> None:
        """
        :param ssl_client_fingerprint: Заголовок выставляется по результату успешного прохождения mTLS.
        :param base_url: URL-адрес API
        :param session: Экземпляр сессии
        :param is_async: Асинхронное выполнение запросов
        """

        self.ssl_client_fingerprint = ssl_client_fingerprint
        self.headers = {
            'ssl-client-fingerprint': self.ssl_client_fingerprint,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }

        self.base_url = base_url
        if not self.base_url[-1] == '/':
            self.base_url += '/'

        self.session = session or (aiohttp.ClientSession() if is_async else requests.Session())
        self.is_async = is_async
        self.logger = logging.getLogger(__name__)

        Connection.__init__(self, self.session, self.headers, self.logger, self.is_async)

    @classmethod
    def Async(cls,
              ssl_client_fingerprint: str,
              base_url: Optional[str] = BASE_RECEIPT_URL,
              session: Union[aiohttp.ClientSession, requests.Session] = None, ):
        """
        Returns the client in async mode.
               :param ssl_client_fingerprint: Заголовок выставляется по результату успешного прохождения mTLS.
        :param base_url: URL-адрес API
        :param session: Экземпляр сессии
        """
        return cls(ssl_client_fingerprint=ssl_client_fingerprint,
                   base_url=base_url,
                   session=session,
                   is_async=True)

    def health(self, **kwargs) -> dict:
        """
        Проверяет базовую работоспособность сервиса
        https://www.inplat-tech.ru/docs/arp/#tag/Health
        """
        url = f"{self.base_url}health"
        return self._request_model(url, data={**kwargs}, method='GET')

    def fiscal_receipt_generation(self,
                                  operation_id: str,
                                  date_time: str,
                                  cash_amount: int,
                                  card_amount: int,
                                  phone_number: str,
                                  items: list[dict],
                                  payment_id: str = None,
                                  receipt_type: int = 0, ) -> dict:
        """
        Fiscal Receipt Generation
        https://www.inplat-tech.ru/docs/arp/#tag/fiscal_receipt_generation/operation/fiscal_receipt_generation_fiscal_receipt_generation_post

        :param payment_id: Уникальный идентификатор платежа ЭПС
        :param operation_id: Уникальный идентификатор опреации по чеку
        :param date_time: Время платежа
        :param receipt_type: Тип чека: 0 - Sale; 1 - Prepaid
        :param cash_amount: Сумма оплаты наличными, в тийин
        :param card_amount: Сумма оплаты по карте, в тийин
        :param phone_number: Номер телефона клиента
        :param items: Список товаров
        """
        url = f"{self.base_url}fiscal_receipt_generation"
        data = {"operation_id": operation_id,
                "date_time": date_time,
                "receipt_type": receipt_type,
                "cash_amount": cash_amount,
                "card_amount": card_amount,
                "phone_number": phone_number,
                "items": items, }
        if payment_id:
            data['payment_id'] = payment_id

        return self._request_model(url, data=data)

    def fiscal_receipt_refund(self,
                              operation_id: str,
                              date_time: str,
                              cash_amount: int,
                              card_amount: int,
                              items: list[dict],
                              payment_id: str = None,
                              receipt_type: int = 0, ) -> dict:
        """
        Fiscal Receipt Refund
        https://www.inplat-tech.ru/docs/arp/#tag/fiscal_receipt_refund/operation/fiscal_receipt_refund_fiscal_receipt_refund_post

        :param payment_id: Уникальный идентификатор платежа ЭПС
        :param operation_id: Уникальный идентификатор опреации по чеку
        :param date_time: Время платежа
        :param receipt_type: Тип чека: 0 - Sale; 1 - Prepaid
        :param cash_amount: Сумма оплаты наличными, в тийин
        :param card_amount: Сумма оплаты по карте, в тийин
        :param items: Список товаров
        """
        url = f"{self.base_url}fiscal_receipt_refund"
        data = {"operation_id": operation_id,
                "date_time": date_time,
                "receipt_type": receipt_type,
                "cash_amount": cash_amount,
                "card_amount": card_amount,
                "items": items, }
        if payment_id:
            data['payment_id'] = payment_id

        return self._request_model(url, data=data)

    def save_qr_code_url(self,
                         operation_id: str,
                         qr_code_url: str,
                         amount: int) -> dict:
        """
        Fiscal Receipt Refund
        https://www.inplat-tech.ru/docs/arp/#tag/save_qr_code_url

        :param operation_id: Уникальный идентификатор опреации по чеку
        :param qr_code_url: QR ссылка
        :param amount: Сумма в тийин. Следует заполнять только в том случае, если проводитсяадаптивный платеж, то есть часть суммы была оплачена через приложение Uzum, остальная часть наличными средствами.
        """
        url = f"{self.base_url}save_qr_code_url"
        data = {"operation_id": operation_id,
                "qr_code_url": qr_code_url,
                "amount": amount, }

        return self._request_model(url, data=data)

    def __repr__(self) -> str:
        return '<Uzum Payments (Receipt Producer) Client async={}>'.format(self.is_async)

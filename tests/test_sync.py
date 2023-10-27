import os
import random

import unittest

import uzum_payments

TERMINAL_ID = os.getenv('terminal_id', '')
SIGNATURE = os.getenv('signature', '')
API_KEY = os.getenv('api_key', '')
BASE_URL = os.getenv('base_url', '')


class TestAsyncClient(unittest.TestCase):
    def setUp(self):
        self.client = uzum_payments.ApiClient(terminal_id=TERMINAL_ID,
                                              api_key=API_KEY,
                                              base_url=BASE_URL)

    def tearDown(self):
        self.client.close()

    def test_get_order_status(self):
        order_id = '5dfa907d-570c-477a-96c1-554638c3f661'
        order_status = self.client.get_order_status(order_id=order_id)

        self.assertEqual(order_status['result']['orderId'], order_id)

    def test_register(self):
        amount = random.randint(1000, 1000000)
        client_id = str(random.randint(10, 10000))
        order_number = str(random.randint(10, 10000))
        currency = 643
        redirect_url = 'https://example.com'
        client_reg = self.client.register(amount,
                                          client_id=client_id,
                                          currency=currency,
                                          order_number=order_number,
                                          success_url=redirect_url,
                                          failure_url=redirect_url)

        self.assertEqual(client_reg['errorCode'], 0)


if __name__ == '__main__':
    unittest.main()

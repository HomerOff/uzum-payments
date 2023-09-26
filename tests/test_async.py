import asyncio
import os
import random

import asynctest

import uzum_payments

TERMINAL_ID = os.getenv('terminal_id', '')
SIGNATURE = os.getenv('signature', '')
API_KEY = os.getenv('api_key', '')
BASE_URL = os.getenv('base_url', '')


class TestAsyncClient(asynctest.TestCase):
    async def setUp(self):
        self.client = uzum_payments.ApiClient.Async(terminal_id=TERMINAL_ID,
                                                    signature=SIGNATURE,
                                                    api_key=API_KEY,
                                                    base_url=BASE_URL)

    async def tearDown(self):
        await self.client.close()
        await asyncio.sleep(2)

    async def test_get_order_status(self):
        order_id = '5dfa907d-570c-477a-96c1-554638c3f661'
        order_status = await self.client.get_order_status(order_id=order_id)

        self.assertEqual(order_status['result']['orderId'], order_id)

    async def test_register(self):
        amount = random.randint(1000, 1000000)
        client_id = str(random.randint(10, 10000))
        order_number = str(random.randint(10, 10000))
        currency = 643
        redirect_url = 'https://example.com'
        client_reg = await self.client.register(amount,
                                                client_id=client_id,
                                                currency=currency,
                                                order_number=order_number,
                                                success_url=redirect_url,
                                                failure_url=redirect_url)

        self.assertEqual(client_reg['errorCode'], 0)


if __name__ == '__main__':
    asynctest.main()

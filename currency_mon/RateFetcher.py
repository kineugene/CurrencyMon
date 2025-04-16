import asyncio
import logging
from enum import Enum
from pip._vendor import requests
from currency_mon import config


class Currency(Enum):
    USD = 1
    EUR = 2
    GBP = 3
    CNY = 4
    RUB = 5


class RateFetcher:
    base_url: str

    def __init__(self, base_currency: Currency, target_currency: Currency):
        self.base_url = "https://v6.exchangerate-api.com/v6/3a3d7703e90eb84f358dd1f6/latest/"
        self.base_currency = base_currency
        self.target_currency = target_currency

    async def get_currency_course(self):
        while config.keep_running:
            logging.info("Запрашиваем данные с сервера.")
            response = requests.get(self.base_url + self.base_currency.name).json()
            config.rates[self.base_currency.name] = response['conversion_rates']
            logging.info(f"Данные получены: {response}")
            await asyncio.sleep(10)

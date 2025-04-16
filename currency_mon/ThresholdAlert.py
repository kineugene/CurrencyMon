import asyncio
from enum import Enum
from currency_mon import config

from currency_mon.RateFetcher import Currency


class AlertCondition(Enum):
    RateGetsHigherThanLimit = 1
    RateGetsLowerThanLimit = 2
    RateChanged = 3


class ThresholdAlert:
    alert_condition: AlertCondition
    target_currency: Currency
    base_currency: Currency
    limit: float

    async def check_rate_by_condition(self):

        while config.keep_running:
            if self.alert_condition == AlertCondition.RateGetsHigherThanLimit:
                if config.rates[self.base_currency.name][self.target_currency.name] > self.limit:
                    print(f"Курс превысил значение {self.limit}! Текущее значение:",
                          config.rates[self.base_currency.name][self.target_currency.name])
            if self.alert_condition == AlertCondition.RateGetsLowerThanLimit:
                if config.rates[self.base_currency.name][self.target_currency.name] < self.limit:
                    print(f"Курс снизился ниже значения {self.limit}! Текущее значение:",
                          config.rates[self.base_currency.name][self.target_currency.name])
            if self.alert_condition == AlertCondition.RateChanged:
                if config.rates[self.base_currency.name][self.target_currency.name] != self.limit:
                    self.limit = config.rates[self.base_currency.name][self.target_currency.name]
                    print("Курс изменился! Текущий курс:",
                          config.rates[self.base_currency.name][self.target_currency.name])

            await asyncio.sleep(10)

    def __init__(self, base_currency: Currency, target_currency: Currency, alert_condition: AlertCondition,
                 limit: float = None):
        self.base_currency = base_currency
        self.target_currency = target_currency
        self.alert_condition = alert_condition
        self.limit = limit


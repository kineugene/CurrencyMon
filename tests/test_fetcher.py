import asyncio
import logging
from time import sleep

from currency_mon import config
from currency_mon.RateFetcher import RateFetcher, Currency


def test_fetch_some():
    fetcher = RateFetcher(Currency.RUB, Currency.EUR)
    rates = dict.copy(config.rates)
    logging.info(f"Сохранил текущее значение rates: {rates}")
    logging.info("Запустил поток")

    async def stop_running():
        logging.info("жду секунду")
        await asyncio.sleep(1)
        config.keep_running = False

    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(stop_running()), fetcher.get_currency_course()]
    tasks_for_wait = asyncio.wait(tasks)
    ioloop.run_until_complete(tasks_for_wait)
    ioloop.close()

    logging.info("Проверяю rates")
    assert rates != config.rates
    logging.info(f"Rates: {rates}")
    config.keep_running = False

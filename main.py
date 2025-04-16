import asyncio
import concurrent
import logging

import config
from RateFetcher import RateFetcher, Currency
from ThresholdAlert import ThresholdAlert, AlertCondition

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

    currencies = ["USD", "EUR", "GBP", "CNY"]

    choose_currency_message = "Выберите валюты для наблюдения:\n"
    for i in range(len(currencies)):
        choose_currency_message += str(i + 1) + ". " + currencies[i] + "\n"

    chosen_currency: str
    all_rules_accepted = False

    while not all_rules_accepted:
        chosen_currency = input(choose_currency_message)
        if not chosen_currency.isdigit():
            print("Вы ввели нечисловое значение. Выберите числовое значение из списка./n")
        elif not (0 < int(chosen_currency) <= len(currencies)):
            print("Вы ввели значение выходящее за диапазон значений. Выберите числовое значение из списка./n")
        else:
            all_rules_accepted = True

    print("Выбранный вариант: ", chosen_currency, currencies[int(chosen_currency) - 1])

    target_currency = Currency(int(chosen_currency))
    alert_condition = ""
    all_rules_accepted = False

    while not all_rules_accepted:
        currencies_clause_message = """
Выберите условие при котором будет приходить уведомление:
1. Курс превысил значение
2. Курс упал ниже значения
3. Курс изменился\n"""
        alert_condition = input(currencies_clause_message)
        if not alert_condition.isdigit():
            print("Вы ввели нечисловое значение. Выберите числовое значение из списка./n")
        elif not (0 < int(alert_condition) <= 3):
            print("Вы ввели значение выходящее за диапазон значений. Выберите числовое значение из списка./n")
        else:
            all_rules_accepted = True

    currency_clause_value = ""

    rate_fetcher = RateFetcher(Currency.RUB, Currency.EUR)

    if int(alert_condition) in [1, 2]:
        currency_clause_value = input("Введите пороговое значение: ")
        if not currency_clause_value.isdigit():
            print("Вы ввели нечисловое значение. Введите числовое значение./n")

    alert_condition = AlertCondition(int(alert_condition))
    alert = ThresholdAlert(base_currency=Currency.RUB, target_currency=target_currency,
                           alert_condition=alert_condition, limit=float(currency_clause_value))


    async def stop_running(loop):
        pool = concurrent.futures.ThreadPoolExecutor()
        while config.keep_running:
            is_stop = await loop.run_in_executor(pool, input,
                                                 "Type 'stop' to stop running.\n")
            if is_stop == 'stop':
                config.keep_running = False
                print("Stopping the process...")


    logging.info(
        "Собираем все задачи на параллельное исполнение: stop_running(), get_currency_course(), "
        "check_rate_by_condition()")
    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(stop_running(ioloop)),
             ioloop.create_task(rate_fetcher.get_currency_course()),
             ioloop.create_task(alert.check_rate_by_condition())]
    tasks_for_wait = asyncio.wait(tasks)
    ioloop.run_until_complete(tasks_for_wait)
    ioloop.close()

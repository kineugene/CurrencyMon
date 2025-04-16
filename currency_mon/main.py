import asyncio
import concurrent
import logging

from currency_mon import config
from currency_mon.RateFetcher import RateFetcher, Currency
from currency_mon.ThresholdAlert import ThresholdAlert, AlertCondition

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

    currencies = Currency._member_names_

    choose_currency_message = f"Выберите валюты для наблюдения:\n"
    for cur in Currency.__iter__():
        choose_currency_message += f"{cur.value}. {cur.name}\n"

    target_currency: Currency
    all_rules_accepted = False
    while not all_rules_accepted:
        currency = input(choose_currency_message)
        if not currency.isdigit():
            print("Вы ввели нечисловое значение. Выберите числовое значение из списка./n")
        elif not (0 < int(currency) <= len(currencies)):
            print("Вы ввели значение выходящее за диапазон значений. Выберите числовое значение из списка./n")
        else:
            target_currency = Currency(int(currency))
            logging.info(f"Выбранный вариант: {target_currency.value}. {target_currency.name}")
            all_rules_accepted = True

    alert_condition: AlertCondition
    all_rules_accepted = False
    while not all_rules_accepted:
        currencies_clause_message = """
Выберите условие при котором будет приходить уведомление:
1. Курс превысил значение
2. Курс упал ниже значения
3. Курс изменился\n"""
        alert = input(currencies_clause_message)
        if not alert.isdigit():
            print("Вы ввели нечисловое значение. Выберите числовое значение из списка./n")
        elif not (0 < int(alert) <= 3):
            print("Вы ввели значение выходящее за диапазон значений. Выберите числовое значение из списка./n")
        else:
            alert_condition = AlertCondition(int(alert))
            logging.info(f"Выбрано условие для оповещения: {alert_condition.value}. {alert_condition.name}")
            all_rules_accepted = True

    currency_clause_value = ""
    all_rules_accepted = False

    if alert_condition in [AlertCondition.RateGetsLowerThanLimit, AlertCondition.RateGetsHigherThanLimit]:
        while not all_rules_accepted:
            currency_clause_value = input("Введите пороговое значение: ")
            if not currency_clause_value.isdigit():
                print("Вы ввели нечисловое значение. Введите числовое значение./n")
            else:
                all_rules_accepted = True


    async def stop_running(loop):
        pool = concurrent.futures.ThreadPoolExecutor()
        while config.keep_running:
            is_stop = await loop.run_in_executor(pool, input,
                                                 "Type 'stop' to stop running.\n")
            if is_stop == 'stop':
                config.keep_running = False
                print("Stopping the process...")


    rate_fetcher = RateFetcher(Currency.RUB, Currency.EUR)
    alert = ThresholdAlert(base_currency=Currency.RUB, target_currency=target_currency,
                           alert_condition=alert_condition, limit=float(currency_clause_value))

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

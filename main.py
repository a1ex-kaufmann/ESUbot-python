# import random
import api.livecoin
import modules.Analysis as Analysis
import modules.mymath as my_math
import modules.visualization as visualization
import logging
import traceback
import datetime
import time

"""Вывод сообщения одновременно в лог и консоль"""


def message(msg):
    logging.info(msg)
    print(datetime.datetime.now(), msg)


"""
SAMPLE - размер выборки для перестроения линии тренда
FIRST - размер выборки, импортируемый из input.txt
"""
SAMPLE = 420
FIRST = 0
MIN_DIFFERENCE = 0.0001
MAX_ORDER_COUNT = 10
MIN_VOLUME_OF_ORDER = 0.0001
mode = ''  # sell / buy

# получаем настройки из config'a
show_graphics = True
ticker_time = 2

# подготавливаем файл для логгирования
logging.basicConfig(filename="trading_process.txt", format=u'[%(asctime)s] %(message)s' , level=logging.INFO)

# импортируем котировки из текстового файла, если требуется
reading_line = open("input.txt", "r")
imported_course = my_math.read_file_txt(reading_line)
course_values = list(imported_course[:FIRST])

# инициализируем сущности анализа и графического представления
analysis = Analysis.Analysis(course_values=course_values, warning_zone_size=0.25, number_of_extremes=1)
if show_graphics:
    chart = visualization.Plot(course_values)

'''
ПОЗЖЕ ЗДЕСЬ БУДЕТ БЛОК ИНИЦИАЛИЗАЦИИ
'''

breaking = False
add_iterator = 0
i = 0
try:
    while True:
        add_iterator += 1

        if FIRST > i:
            course_values.append([i, imported_course[i]][1])
        else:
            # принимаем значения цены, бид и аск из стакана
            summary = api.livecoin.pair_cost_summary()
            cost, ask, bid = summary
            message("New values: " + "cost=" + str(cost) + " ask=" + str(ask) + " bid=" + str(bid))
            course_values.append([i, cost])
            bid = bid + MIN_DIFFERENCE
            ask = ask - MIN_DIFFERENCE

        if show_graphics:
            chart.draw_point(course_values[i], analysis.is_point_in_corridor_status(course_values[i]))

        if analysis.get_trend_was_built() and add_iterator != SAMPLE:
            if analysis.type_of_trend == 'rising':
                if analysis.is_point_in_corridor_status(course_values[i]) == 3 and not breaking:
                    breaking = True
                    mode = 'sell'
                    "ОТМЕНИТЬ ОРДЕРА"
                    message("ПРОБИТИЕ СНИЗУ, ОТМЕНЯЕМ ОРДЕРА")
                    info = api.livecoin.cancel_open_orders()
                    message(info)
                elif analysis.is_point_in_corridor_status(course_values[i]) != 3 and breaking:
                    breaking = False
                    mode = 'buy'
                    message("ПРОБИТИЕ СНИЗУ ОТМЕНИЛОСЬ")
            elif analysis.type_of_trend == 'downward':
                if analysis.is_point_in_corridor_status(course_values[i]) == 0 and not breaking:
                    breaking = True
                    mode = 'buy'
                    "ОТМЕНИТЬ ОРДЕРА"
                    message("ПРОБИТИЕ НАВЕРХУ, ОТМЕНЯЕМ ОРДЕРА")
                    info = api.livecoin.cancel_open_orders()
                    message(info)
                elif analysis.is_point_in_corridor_status(course_values[i]) != 0 and breaking:
                    breaking = False
                    mode = 'sell'
                    message("ПРОБИТИЕ НАВЕРХУ ОТМЕНИЛОСЬ")

        if add_iterator == SAMPLE:
            breaking = False
            add_iterator = 0
            analysis.calculate_trend_line(degree=1, sample=SAMPLE)
            analysis.calculate_support_corridor(sample=SAMPLE)
            message("Trend line has been rebuilt: " + str(analysis.get_trend_coefficients()) +
                    " alpha = " + str(analysis.get_trend_coefficients()[0]) +
                    " type_of_trend=" + str(analysis.get_type_of_trend()) +
                    " trend_was_changed=" + str(analysis.get_trend_was_changed()))
            if show_graphics:
                chart.draw_corridor(analysis.get_trend_coefficients(), analysis.get_support_top_coefficients(),
                                    analysis.get_support_bot_coefficients(),
                                    analysis.get_warning_top_coefficients(),
                                    analysis.get_warning_bot_coefficients(),
                                    course_values[len(course_values) - SAMPLE:])

            if analysis.get_type_of_trend() == 'rising':
                mode = 'buy'
            elif analysis.get_type_of_trend() == 'downward':
                mode = 'sell'

            if analysis.get_trend_was_changed():
                message("ТРЕНД БЫЛ ИЗМЕНЁН. СНИМАЕМ ОРДЕРА")
                info = api.livecoin.cancel_open_orders()
                message(info)

            time.sleep(1)
            info = api.livecoin.available_balances('BTC', 'USD')
            message('balance: ' + str(info))
            balance_currency_1 = info[0]
            balance_currency_2 = info[1]

            time.sleep(1)
            message("ВЫСТАВЛЯЕМ ОРДЕР НА " + mode)
            if mode == 'buy':
                cost = bid
                info = api.livecoin.buy_currency(round(cost), round(0.7*(balance_currency_2 - 0.0018 * balance_currency_2) / cost, 5))
                message(info)
            elif mode == 'sell':
                cost = ask
                info = api.livecoin.sell_currency(round(cost,8), round(0.7*balance_currency_1, 5))
                message(info)
        i += 1
        if show_graphics:
            chart.pause(ticker_time)
        else:
            time.sleep(ticker_time)
except Exception:
    print(traceback.format_exc())
    logging.exception("Error!")

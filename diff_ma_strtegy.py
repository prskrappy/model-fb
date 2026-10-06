import pandas as pd
from datetime import datetime, timedelta


def strategy(_inp_link, _config):

    _purchase_list = []
    _purchase = {}
    _in_order_long = False
    _in_order_short = False
    _data = read_data(_inp_link)
    _capital = float(_config["money_to_buy"])
    _capital_max = _capital

    # отсупаем до напитания индикаторов - _config['sma_frame(close)']
    # считаем сумму для простой скользящей (по закрытию)
    _sma_sum = 0
    for i in range(_config["sma_frame(close)"]):
        _sma_sum += float(_data[i]["close"])

    # считаем экспоненциальную среднюю (по максимуму бара)
    _df = pd.DataFrame(
        {
            "maximum": [
                elem["maximum"]
                for elem in _data[
                    _config["sma_frame(close)"]
                    - _config["ema_frame(maximum)"] : _config["sma_frame(close)"]
                ]
            ]
        }
    )
    _df["ema"] = (
        _df["maximum"]
        .ewm(span=_config["ema_frame(maximum)"], adjust=False, min_periods=5)
        .mean()
    )
    _ema = _df.values[-1][1]

    for i in range(_config["sma_frame(close)"], len(_data)):
        # индикатор простой скользящей (по закрытию)
        _sma_sum = (
            _sma_sum
            - float(_data[i - _config["sma_frame(close)"]]["close"])
            + float(_data[i]["close"])
        )
        _sma_av = _sma_sum / _config["sma_frame(close)"]

        # индикатор экспоненциальную среднюю (по максимуму бара)
        _weight_factor = 2 / (_config["ema_frame(maximum)"] + 1)
        _ema = _ema + _weight_factor * (float(_data[i]["maximum"]) - _ema)

        # проверяем условие, что хватает денег на лот
        _lot_price = float(_data[i]["close"]) * float(_config["shares_in_lot"])
        if _capital > _lot_price:
            # стратегия с реинвестированием
            if _config["reinvestition"]:
                # лонг
                if _config["long_flag"]:
                    # заходим в лонг
                    if (
                        (_sma_av < _ema)
                        and not (_in_order_long)
                        and not (_in_order_short)
                    ):
                        _purchase = long_input(
                            _data[i + 1], _config, _capital, _sma_av, _ema, 0
                        )
                        _in_order_long = True
                    # выходим из лонга
                    if (_sma_av > _ema) and (_in_order_long) and not (_in_order_short):
                        _purchase, _capital, _capital_max = long_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital_max,
                            _capital_max,
                            0,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_long = False
                # шорт
                if _config["short_flag"]:
                    # заходим в шорт
                    if (
                        (_sma_av > _ema)
                        and not (_in_order_short)
                        and not (_in_order_long)
                    ):
                        _purchase = short_input(
                            _data[i + 1], _config, _capital, _sma_av, _ema, 0
                        )
                        _in_order_short = True
                    # выходим из шорта
                    if (_sma_av < _ema) and _in_order_short and not (_in_order_long):
                        _purchase, _capital, _capital_max = short_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital,
                            _capital_max,
                            _capital_max,
                            0,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_short = False

            # стратегия без реинвестирования
            else:
                # деньги, не участвующие в сделке
                _frozen_money = 0
                if _capital > float(_config["money_to_buy"]):
                    _frozen_money = _capital - float(_config["money_to_buy"])
                # лонг
                if _config["long_flag"]:
                    # заходим в лонг
                    if (
                        (_sma_av < _ema)
                        and not (_in_order_long)
                        and not (_in_order_short)
                    ):
                        _purchase = long_input(
                            _data[i + 1],
                            _config,
                            _capital,
                            _sma_av,
                            _ema,
                            _frozen_money,
                        )
                        _in_order_long = True
                    # выходим из лонга
                    if (_sma_av > _ema) and (_in_order_long) and not (_in_order_short):
                        _purchase, _capital, _capital_max = long_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital_max,
                            _config["money_to_buy"],
                            _frozen_money,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_long = False
                # шорт
                if _config["short_flag"]:
                    # заходим в шорт
                    if (
                        (_sma_av > _ema)
                        and not (_in_order_short)
                        and not (_in_order_long)
                    ):
                        _purchase = short_input(
                            _data[i + 1],
                            _config,
                            _capital,
                            _sma_av,
                            _ema,
                            _frozen_money,
                        )
                        _in_order_short = True
                    # выходим из шорта
                    if (_sma_av < _ema) and _in_order_short and not (_in_order_long):
                        _purchase, _capital, _capital_max = short_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital,
                            _capital_max,
                            _config["money_to_buy"],
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_short = False

    # добавляем последнюю сделку, если она не была закрыта ранее
    # if _in_order_long:
    #     _purchase_list.append(_purchase)
    # if _in_order_short:
    #     _purchase_list.append(_purchase)

    return _purchase_list


def long_input(_cur_data, _config, _cur_capital, _sma, _ema, _cur_frozen_money):
    _purchase_temp = {}
    _cur_lot_prize = float(_cur_data["open"]) * float(
        _config["shares_in_lot"]
    )  #!покупаем по открытию

    _purchase_temp["ticker"] = _cur_data["ticker"]
    _purchase_temp["buy_date"] = _cur_data["date"]
    _purchase_temp["buy_time"] = _cur_data["time"]
    _purchase_temp["type"] = "long"
    _purchase_temp["sma(close)_in"] = _sma
    _purchase_temp["ema(high)_in"] = _ema
    _purchase_temp["buy_price"] = float(_cur_data["open"])
    _purchase_temp["volume(lots)"] = (
        (_cur_capital - _cur_frozen_money)
        * float(100 - _config["comission"])
        / 100
        // float(_cur_lot_prize)
    )
    _purchase_temp["volume(shares)"] = _purchase_temp["volume(lots)"] * float(
        _config["shares_in_lot"]
    )
    _purchase_temp["shares_in_lot"] = float(_config["shares_in_lot"])
    _purchase_temp["money_in_order"] = _purchase_temp["volume(lots)"] * _cur_lot_prize
    _purchase_temp["frozen_money"] = _cur_frozen_money  # убрать?
    _purchase_temp["comission_buy"] = (
        _purchase_temp["money_in_order"] * float(_config["comission"]) / 100
    )
    _purchase_temp["resid"] = (
        _cur_capital
        - _cur_frozen_money
        - _purchase_temp["comission_buy"]
        - _purchase_temp["money_in_order"]
    )

    return _purchase_temp


def long_output(
    _cur_data,
    _purchase,
    _config,
    _sma,
    _ema,
    _capital_max,
    _capital_for_drawdawn,
    _cur_frozen_money,
):
    _cur_purchase = _purchase
    _cur_lot_prize = float(_cur_data["open"]) * float(
        _config["shares_in_lot"]
    )  #!покупаем по открытию

    _cur_purchase["sell_date"] = _cur_data["date"]
    _cur_purchase["sell_time"] = _cur_data["time"]
    _cur_purchase["sma(close)_out"] = _sma
    _cur_purchase["ema(high)_out"] = _ema
    _cur_purchase["sell_price"] = float(_cur_data["open"])
    _cur_purchase["sell_money"] = (
        float(_cur_purchase["volume(lots)"] * _cur_lot_prize)
        * float(100 - _config["comission"])
        / 100
    )
    _cur_purchase["comission_sell"] = (
        float(_cur_purchase["volume(lots)"] * _cur_lot_prize)
        * float(_config["comission"])
        / 100
    )
    _cur_purchase["comission_deal"] = (
        _cur_purchase["comission_buy"] + _cur_purchase["comission_sell"]
    )
    _capital = _cur_purchase["resid"] + _cur_purchase["sell_money"] + _cur_frozen_money
    _cur_purchase["capital"] = _capital

    _capital_max = max(_capital_max, _capital)
    _drawdawn = _capital_max - _capital

    _cur_purchase["drawdawn"] = _drawdawn
    _cur_purchase["drawdawn_%"] = _drawdawn / (_capital_for_drawdawn) * 100

    return _cur_purchase, _capital, _capital_max


def short_input(_cur_data, _config, _cur_capital, _sma, _ema, _cur_frozen_money):
    _purchase_temp = {}
    _cur_lot_prize = float(_cur_data["open"]) * float(
        _config["shares_in_lot"]
    )  #!покупаем по открытию

    _purchase_temp["ticker"] = _cur_data["ticker"]
    _purchase_temp["buy_date"] = _cur_data["date"]
    _purchase_temp["buy_time"] = _cur_data["time"]
    _purchase_temp["type"] = "short"
    _purchase_temp["sma(close)_in"] = _sma
    _purchase_temp["ema(high)_in"] = _ema
    _purchase_temp["buy_price"] = float(_cur_data["open"])
    _purchase_temp["volume(lots)"] = (
        (_cur_capital - _cur_frozen_money)
        * float(100 - _config["comission"])
        / 100
        // float(_cur_lot_prize)
    )
    _purchase_temp["volume(shares)"] = _purchase_temp["volume(lots)"] * float(
        _config["shares_in_lot"]
    )
    _purchase_temp["shares_in_lot"] = float(_config["shares_in_lot"])
    _purchase_temp["money_in_order"] = _purchase_temp["volume(lots)"] * _cur_lot_prize
    _purchase_temp["frozen_money"] = _cur_frozen_money
    _purchase_temp["comission_buy"] = (
        _purchase_temp["money_in_order"] * float(_config["comission"]) / 100
    )
    _purchase_temp["resid"] = (
        _cur_capital
        - _cur_frozen_money
        - _purchase_temp["comission_buy"]
        - _purchase_temp["money_in_order"]
    )

    return _purchase_temp


def short_output(
    _cur_data,
    _purchase,
    _config,
    _sma,
    _ema,
    _capital,
    _capital_max,
    _capital_for_drawdawn,
):
    _cur_purchase = _purchase
    _cur_lot_prize = float(_cur_data["open"]) * float(
        _config["shares_in_lot"]
    )  #!покупаем по открытию

    _cur_purchase["sell_date"] = _cur_data["date"]
    _cur_purchase["sell_time"] = _cur_data["time"]
    _cur_purchase["sma(close)_out"] = _sma
    _cur_purchase["ema(high)_out"] = _ema
    _cur_purchase["sell_price"] = float(_cur_data["open"])
    _cur_purchase["sell_money"] = float(_cur_purchase["volume(lots)"] * _cur_lot_prize)
    _cur_purchase["comission_sell"] = (
        float(_cur_purchase["volume(lots)"] * _cur_lot_prize)
        * float(_config["comission"])
        / 100
    )
    _cur_purchase["comission_deal"] = (
        _cur_purchase["comission_buy"] + _cur_purchase["comission_sell"]
    )
    _capital = (
        _capital
        - _cur_purchase["comission_deal"]
        + _cur_purchase["money_in_order"]
        - _purchase["sell_money"]
    )  # + _cur_purchase['resid'] + _cur_frozen_money
    _cur_purchase["capital"] = _capital

    _capital_max = max(_capital_max, _capital)
    _drawdawn = _capital_max - _capital

    _cur_purchase["drawdawn"] = _drawdawn
    _cur_purchase["drawdawn_%"] = _drawdawn / (_capital_for_drawdawn) * 100

    return _cur_purchase, _capital, _capital_max


def read_data(_inp_link):
    _data = []

    f = open("processed_files/moving average/{}".format(_inp_link), "r")
    for line in f:
        _slovar = {}
        _strok = line.split("; ")

        for elem in _strok[:-1]:
            _slovar[elem.split(" ")[0]] = elem.split(" ")[1]

        _data.append(_slovar)

    return _data


def write_data_excel(_inp_link, _config):

    dt = strategy(_inp_link, _config)
    _day_rep = day_report(dt)
    _d_cap = pd.DataFrame(
        [
            {
                "date": (elem["sell_date"] + " " + elem["sell_time"]),
                "capital": elem["capital"],
            }
            for elem in dt
        ]
    )
    _d_dd = pd.DataFrame(
        [
            {
                "date": (elem["sell_date"] + " " + elem["sell_time"]),
                "drawdawn": elem["drawdawn"],
                "drawdawn_%": elem["drawdawn_%"],
            }
            for elem in dt
        ]
    )
    _dr = pd.DataFrame(
        [
            {
                "date": elem["date"],
                "capital" + elem["ticker"]: elem["capital"],
                "drawdawn" + elem["ticker"]: elem["drawdawn"],
            }
            for elem in _day_rep
        ]
    )
    _dt = pd.DataFrame(dt)

    with pd.ExcelWriter(
        "strategy_log_files/moving average/{}_logs.xlsx".format(
            _inp_link.replace(".txt", "")
        )
    ) as writer:

        _dt.to_excel(writer, sheet_name="purchase_sheet")
        _d_cap.to_excel(writer, sheet_name="Sheet_capital")
        _d_dd.to_excel(writer, sheet_name="Sheet_drawdawn")
        _dr.to_excel(writer, sheet_name="Day_report")

    return


# формирование отчёта для совокупного анализа стратегий
def day_report(_inp_list):
    _out_list = []

    for i in range(len(_inp_list) - 1):
        cap_slice = []
        if _inp_list[i]["sell_date"] != _inp_list[i + 1]["sell_date"]:
            _capital = _inp_list[i]["capital"]
            _drawdawn = _inp_list[i]["drawdawn"]

            start_date = datetime(
                int(_inp_list[i]["sell_date"][:4]),
                int(_inp_list[i]["sell_date"][5:7]),
                int(_inp_list[i]["sell_date"][8:]),
            )
            end_date = datetime(
                int(_inp_list[i + 1]["sell_date"][:4]),
                int(_inp_list[i + 1]["sell_date"][5:7]),
                int(_inp_list[i + 1]["sell_date"][8:]),
            )

            cap_slice = [
                {
                    "ticker": _inp_list[i]["ticker"],
                    "date": (start_date + timedelta(days=x)).strftime("%Y-%m-%d"),
                    "capital": _capital,
                    "drawdawn": _drawdawn,
                }
                for x in range((end_date - start_date).days)
            ]
            _out_list.extend(cap_slice)

    return _out_list


def write_data_txt(_inp_link, _config):

    _data = strategy(_inp_link, _config)

    f = open(
        "strategy_log_files/moving average/{}".format(_inp_link), "w", encoding="utf-8"
    )
    for elem in _data:
        _strok = ""
        for key, value in elem.items():
            _strok += str(key) + " " + str(value) + "; "
        f.write(_strok + "\n")
    f.close()

    return


# дубль


def strategy_plus_hist(_inp_link, _config):

    _purchase_list = []
    _purchase = {}
    _in_order_long = False
    _in_order_short = False
    _data = read_data_plus_hist(_inp_link)
    _capital = float(_config["money_to_buy"])
    _capital_max = _capital

    # отсупаем до напитания индикаторов - _config['sma_frame(close)']
    # считаем сумму для простой скользящей (по закрытию)
    _sma_sum = 0
    for i in range(_config["sma_frame(close)"]):
        _sma_sum += float(_data[i]["close"])

    # считаем экспоненциальную среднюю (по максимуму бара)
    _df = pd.DataFrame(
        {
            "maximum": [
                elem["maximum"]
                for elem in _data[
                    _config["sma_frame(close)"]
                    - _config["ema_frame(maximum)"] : _config["sma_frame(close)"]
                ]
            ]
        }
    )
    _df["ema"] = (
        _df["maximum"]
        .ewm(span=_config["ema_frame(maximum)"], adjust=False, min_periods=5)
        .mean()
    )
    _ema = _df.values[-1][1]

    for i in range(_config["sma_frame(close)"], len(_data)):
        # индикатор простой скользящей (по закрытию)
        _sma_sum = (
            _sma_sum
            - float(_data[i - _config["sma_frame(close)"]]["close"])
            + float(_data[i]["close"])
        )
        _sma_av = _sma_sum / _config["sma_frame(close)"]

        # индикатор экспоненциальную среднюю (по максимуму бара)
        _weight_factor = 2 / (_config["ema_frame(maximum)"] + 1)
        _ema = _ema + _weight_factor * (float(_data[i]["maximum"]) - _ema)

        # проверяем условие, что хватает денег на лот
        _lot_price = float(_data[i]["close"]) * float(_config["shares_in_lot"])
        if _capital > _lot_price:
            # стратегия с реинвестированием
            if _config["reinvestition"]:
                # лонг
                if _config["long_flag"]:
                    # заходим в лонг
                    if (
                        (_sma_av < _ema)
                        and not (_in_order_long)
                        and not (_in_order_short)
                    ):
                        _purchase = long_input(
                            _data[i + 1], _config, _capital, _sma_av, _ema, 0
                        )
                        _in_order_long = True
                    # выходим из лонга
                    if (_sma_av > _ema) and (_in_order_long) and not (_in_order_short):
                        _purchase, _capital, _capital_max = long_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital_max,
                            _capital_max,
                            0,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_long = False
                # шорт
                if _config["short_flag"]:
                    # заходим в шорт
                    if (
                        (_sma_av > _ema)
                        and not (_in_order_short)
                        and not (_in_order_long)
                    ):
                        _purchase = short_input(
                            _data[i + 1], _config, _capital, _sma_av, _ema, 0
                        )
                        _in_order_short = True
                    # выходим из шорта
                    if (_sma_av < _ema) and _in_order_short and not (_in_order_long):
                        _purchase, _capital, _capital_max = short_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital,
                            _capital_max,
                            _capital_max,
                            0,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_short = False

            # стратегия без реинвестирования
            else:
                # деньги, не участвующие в сделке
                _frozen_money = 0
                if _capital > float(_config["money_to_buy"]):
                    _frozen_money = _capital - float(_config["money_to_buy"])
                # лонг
                if _config["long_flag"]:
                    # заходим в лонг
                    if (
                        (_sma_av < _ema)
                        and not (_in_order_long)
                        and not (_in_order_short)
                    ):
                        _purchase = long_input(
                            _data[i + 1],
                            _config,
                            _capital,
                            _sma_av,
                            _ema,
                            _frozen_money,
                        )
                        _in_order_long = True
                    # выходим из лонга
                    if (_sma_av > _ema) and (_in_order_long) and not (_in_order_short):
                        _purchase, _capital, _capital_max = long_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital_max,
                            _config["money_to_buy"],
                            _frozen_money,
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_long = False
                # шорт
                if _config["short_flag"]:
                    # заходим в шорт
                    if (
                        (_sma_av > _ema)
                        and not (_in_order_short)
                        and not (_in_order_long)
                    ):
                        _purchase = short_input(
                            _data[i + 1],
                            _config,
                            _capital,
                            _sma_av,
                            _ema,
                            _frozen_money,
                        )
                        _in_order_short = True
                    # выходим из шорта
                    if (_sma_av < _ema) and _in_order_short and not (_in_order_long):
                        _purchase, _capital, _capital_max = short_output(
                            _data[i + 1],
                            _purchase,
                            _config,
                            _sma_av,
                            _ema,
                            _capital,
                            _capital_max,
                            _config["money_to_buy"],
                        )
                        _purchase_list.append(_purchase)
                        _purchase = {}
                        _in_order_short = False

    # добавляем последнюю сделку, если она не была закрыта ранее
    # if _in_order_long:
    #     _purchase_list.append(_purchase)
    # if _in_order_short:
    #     _purchase_list.append(_purchase)

    print("sma", _sma_av, "ema:", _ema)

    return _purchase_list


def read_data_plus_hist(_inp_link):
    _data = []

    f = open("data/hist(proc)/{}".format(_inp_link), "r")
    for line in f:
        _slovar = {}
        _strok = line.split("; ")

        for elem in _strok[:-1]:
            _slovar[elem.split(" ")[0]] = elem.split(" ")[1]

        _data.append(_slovar)

    return _data


def write_data_excel_plus_hist(_inp_link, _config):

    dt = strategy_plus_hist(_inp_link, _config)
    _day_rep = day_report(dt)
    _d_cap = pd.DataFrame(
        [
            {
                "date": (elem["sell_date"] + " " + elem["sell_time"]),
                "capital": elem["capital"],
            }
            for elem in dt
        ]
    )
    _d_dd = pd.DataFrame(
        [
            {
                "date": (elem["sell_date"] + " " + elem["sell_time"]),
                "drawdawn": elem["drawdawn"],
                "drawdawn_%": elem["drawdawn_%"],
            }
            for elem in dt
        ]
    )
    _dr = pd.DataFrame(
        [
            {
                "date": elem["date"],
                "capital" + elem["ticker"]: elem["capital"],
                "drawdawn" + elem["ticker"]: elem["drawdawn"],
            }
            for elem in _day_rep
        ]
    )
    _dt = pd.DataFrame(dt)

    with pd.ExcelWriter(
        "data/strat_res/{}_logs.xlsx".format(_inp_link.replace(".txt", ""))
    ) as writer:

        _dt.to_excel(writer, sheet_name="purchase_sheet")
        _d_cap.to_excel(writer, sheet_name="Sheet_capital")
        _d_dd.to_excel(writer, sheet_name="Sheet_drawdawn")
        _dr.to_excel(writer, sheet_name="Day_report")

    return


config_test = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 20,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 10,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_BR = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 5600,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 570,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_CR = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2600,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 990,  # экспоненциальная средняя (по максимуму)
    "comission": 0.02,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_Eu = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2300,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 620,  # экспоненциальная средняя (по максимуму)
    "comission": 0.02,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_GAZR = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 5200,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 800,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_RTS = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 4400,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 400,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_SBRF = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 4400,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 200,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_Si = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 1600,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 800,  # экспоненциальная средняя (по максимуму)
    "comission": 0.02,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_VTBR = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2200,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 170,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_YNDF = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2000,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 170,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_OZON = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2000,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 170,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

config_NG = {
    "money_to_buy": 1000000,  # стартовый капитал
    "sma_frame(close)": 2700,  # скользящая средняя (по клозу)
    "ema_frame(maximum)": 70,  # экспоненциальная средняя (по максимуму)
    "comission": 0.05,  # комиссия в %
    "shares_in_lot": 1,  # кол-во акций в одном лоте
    "reinvestition": False,  # стратегия с реинвестицией или без
    "long_flag": True,  # флаг на стратегию в лонг
    "short_flag": True,  # флаг на стратегию в шорт
}

# inp_link1 = 'test.txt'
# write_data_excel(inp_link1, config_test)

# inp_link1 = 'BR.txt'
# write_data_excel(inp_link1, config_BR)

# inp_link2 = 'CR.txt'
# write_data_excel(inp_link2, config_CR)

# inp_link3 = 'Eu.txt'
# write_data_excel(inp_link3, config_Eu)

# inp_link4 = 'GAZR.txt'
# write_data_excel(inp_link4, config_GAZR)

# inp_link5 = 'RTS.txt'
# write_data_excel(inp_link5, config_RTS)

# inp_link6 = 'SBRF.txt'
# write_data_excel(inp_link6, config_SBRF)

# inp_link7 = 'Si.txt'
# write_data_excel(inp_link7, config_Si)

# inp_link8 = 'VTBR.txt'
# write_data_excel(inp_link8, config_VTBR)

# inp_link9 = 'YNDF.txt'
# write_data_excel(inp_link9, config_YNDF)

# inp_link10 = 'OZON.txt'
# write_data_excel(inp_link10, config_OZON)

# inp_link11 = 'NG.txt'
# write_data_excel(inp_link11, config_NG)

# inp_link1 = 'test.txt'
# write_data_excel(inp_link1, config_test)

# #склеянная история
# inp_link1 = "BR_old.txt"
# write_data_excel_plus_hist(inp_link1, config_BR)

# inp_link2 = "CNY_old.txt"
# write_data_excel_plus_hist(inp_link2, config_CR)

# inp_link3 = "Eu_old.txt"
# write_data_excel_plus_hist(inp_link3, config_Eu)

# inp_link4 = "GAZR_old.txt"
# write_data_excel_plus_hist(inp_link4, config_GAZR)

# inp_link5 = "RTS_old.txt"
# write_data_excel_plus_hist(inp_link5, config_RTS)

# inp_link6 = "SBRF_old.txt"
# write_data_excel_plus_hist(inp_link6, config_SBRF)

# inp_link7 = "Si_old.txt"
# write_data_excel_plus_hist(inp_link7, config_Si)

# inp_link8 = "VTBR_old.txt"
# write_data_excel_plus_hist(inp_link8, config_VTBR)

# inp_link9 = "YNDF_old.txt"
# write_data_excel_plus_hist(inp_link9, config_YNDF)

# inp_link10 = "OZON_old.txt"
# write_data_excel_plus_hist(inp_link10, config_OZON)

# inp_link11 = "NG_old.txt"
# write_data_excel_plus_hist(inp_link11, config_NG)

# #склеянная история
inp_link1 = "YNDF_old - Copy.txt"
write_data_excel_plus_hist(inp_link1, config_YNDF)

# for tiker in ['BR',
#               "CNY",
#               "Eu",
#               "GAZR",
#               "NG",
#               "OZON",
#               "RTS",
#               "SBRF",
#               "Si",
#               "VTBR",
#               "YNDF"]:
#     inp_link_name = tiker + "_old.txt"
#     config_name = "config" + tiker
#     write_data_excel_plus_hist(inp_link_name, config_name)
"""
GOLD 35,53
BR 51,40
CR 10,55
Eu 23,87
Eu_N 55,99
Gazr 45,82
NG 75,12
OZON 22,79
RTS 54,23
SBRF 40,87
Si 24,53
VTBR 47,15
YNDF 21.85




"""

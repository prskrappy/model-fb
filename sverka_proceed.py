# def analysis_input_data(input_link):
#     f = open(input_link, "r")
#     _situation = []

#     for line in f:
#         _day_data = {}
#         _line_data = line.split(",")
#         _day_data["ticker"] = _line_data[0]
#         _day_data["date"] = (
#             _line_data[2][0:4] + "-" + _line_data[2][4:6] + "-" + _line_data[2][6:]
#         )
#         _day_data["time"] = (
#             _line_data[3][0:2] + ":" + _line_data[3][2:4] + ":" + _line_data[3][4:]
#         )
#         _day_data["open"] = float(_line_data[4])
#         _day_data["maximum"] = float(_line_data[5])
#         _day_data["minimum"] = float(_line_data[6])
#         _day_data["close"] = float(_line_data[7])
#         _situation.append(_day_data)

#     f.close()

#     return _situation


# def get_out_data(link):

#     situation = analysis_input_data("input_files/moving average/{}".format(link))

#     f = open("processed_files/moving average/{}".format(link), "w", encoding="utf-8")
#     for elem in situation:
#         _strok = ""
#         for key, value in elem.items():
#             _strok += str(key) + " " + str(value) + "; "
#         f.write(_strok + "\n")
#     f.close()


def analysis_input_data_plus_hist(input_link):
    f = open(input_link, "r")
    _situation = []

    for line in f:
        _day_data = {}
        _line_data = line.split(",")
        _day_data["ticker"] = _line_data[0]
        _day_data["date"] = (
            _line_data[2][0:4] + "-" + _line_data[2][4:6] + "-" + _line_data[2][6:]
        )
        _day_data["time"] = _line_data[3]
        _day_data["open"] = float(_line_data[4])
        _day_data["maximum"] = float(_line_data[5])
        _day_data["minimum"] = float(_line_data[6])
        _day_data["close"] = float(_line_data[7])
        _situation.append(_day_data)

    f.close()

    return _situation


def get_out_data_plus_hist(link):

    situation = analysis_input_data_plus_hist("data for sverka/newdata/{}".format(link))

    f = open("data for sverka/sverka_proceed/{}".format(link), "w", encoding="utf-8")
    for elem in situation:
        _strok = ""
        for key, value in elem.items():
            _strok += str(key) + " " + str(value) + "; "
        f.write(_strok + "\n")
    f.close()


for tiker in [
    "BR",
    "CNY",
    "Eu",
    "GAZR",
    "NG",
    "OZON",
    "RTS",
    "SBRF",
    "Si",
    "VTBR",
    "YNDF",
]:

    inp_link1 = tiker + "_new.txt"

    print(inp_link1)
    get_out_data_plus_hist(inp_link1)

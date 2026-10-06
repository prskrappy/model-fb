def analysis_input_data(input_link):
    f = open(input_link, "r")
    _situation = []

    for line in f:
        _day_data = {}
        _line_data = line.split(",")
        _day_data["ticker"] = _line_data[0]
        _day_data["date"] = (
            _line_data[2][0:4] + "-" + _line_data[2][4:6] + "-" + _line_data[2][6:]
        )
        _day_data["time"] = (
            _line_data[3][0:2] + ":" + _line_data[3][2:4] + ":" + _line_data[3][4:]
        )
        _day_data["open"] = float(_line_data[4])
        _day_data["maximum"] = float(_line_data[5])
        _day_data["minimum"] = float(_line_data[6])
        _day_data["close"] = float(_line_data[7])
        _situation.append(_day_data)

    f.close()

    return _situation


def get_out_data(link):

    situation = analysis_input_data("input_files/moving average/{}".format(link))

    f = open("processed_files/moving average/{}".format(link), "w", encoding="utf-8")
    for elem in situation:
        _strok = ""
        for key, value in elem.items():
            _strok += str(key) + " " + str(value) + "; "
        f.write(_strok + "\n")
    f.close()


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

    situation = analysis_input_data_plus_hist("data/historical/{}".format(link))

    f = open("data/hist(proc)/{}".format(link), "w", encoding="utf-8")
    for elem in situation:
        _strok = ""
        if int(elem["time"]) >= 100000 and int(elem["time"]) < 185000:
            elem["time"] = (
                elem["time"][0:2] + ":" + elem["time"][2:4] + ":" + elem["time"][4:]
            )
            for key, value in elem.items():
                _strok += str(key) + " " + str(value) + "; "
            f.write(_strok + "\n")
    f.close()


# inp_link1 = 'test.txt'
# get_out_data(inp_link1)

# inp_link1 = "BR.txt"
# get_out_data(inp_link1)

# # убрать в другой портфель
# inp_link2 = "CR.txt"
# get_out_data(inp_link2)

# inp_link4 = "Eu.txt"
# get_out_data(inp_link4)

# # убрать в другой портфель
# inp_link3 = "NG.txt"
# get_out_data(inp_link3)

# inp_link5 = "GAZR.txt"
# get_out_data(inp_link5)

# inp_link6 = "RTS.txt"
# get_out_data(inp_link6)

# inp_link7 = "SBRF.txt"
# get_out_data(inp_link7)

# inp_link8 = "Si.txt"
# get_out_data(inp_link8)

# inp_link9 = "VTBR.txt"
# get_out_data(inp_link9)

# # убрать в другой портфель
# inp_link10 = "YNDF.txt"
# get_out_data(inp_link10)

# # убрать в другой портфель
# inp_link11 = "OZON.txt"
# get_out_data(inp_link11)

# склеинные данные
for tiker in [
    # "BR",
    # "CNY",
    # "Eu",
    # "GAZR",
    # "NG",
    # "OZON",
    # "RTS",
    # "SBRF",
    # "Si",
    # "VTBR",
    "YNDF",
]:
    inp_link1 = tiker + "_old.txt"
    inp_link2 = tiker + "_new.txt"
    inp_link3 = tiker + "_old - Copy.txt"
    print(inp_link1)
    get_out_data_plus_hist(inp_link1)

    print(inp_link2)
    get_out_data_plus_hist(inp_link2)

    print(inp_link3)
    get_out_data_plus_hist(inp_link3)

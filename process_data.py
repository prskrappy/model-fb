import pandas as pd


def read_csv(path):
    data = pd.read_csv(path)
    data.columns = [
        "ticker",
        "per",
        "date",
        "time",
        "open",
        "high",
        "low",
        "close",
        "vol",
    ]
    return data


def process_datetime(data):
    print(data)
    data["datetime"] = pd.to_datetime(
        data["date"].astype(str) + data["time"].astype(str), format="%Y%m%d%H%M%S"
    )
    data["datetime"] = (
        data["datetime"].dt.tz_localize("Europe/Moscow").dt.tz_convert("UTC")
    )
    return data.set_index("datetime")


def drop_unused_columns(data):
    return data.drop(["date", "time", "per"], axis=1)


def filter_by_time(data):
    return data.between_time("07:00", "15:49")


def save_csv(data, path):
    data.to_csv(path)


if __name__ == "__main__":
    tickers = [
        "YNDF",
    ]  # "BR"  # , 'CNY', 'Eu', 'GAZR', 'SBRF', 'Si', 'VTBR', 'YNDF', 'NG']

    for ticker in tickers:
        file_path = f"data/historical/{ticker}_old.txt"
        print(file_path)
        processed_file_path = f"data/historical/{ticker}.csv"
        df = read_csv(file_path)

        df = df.pipe(process_datetime).pipe(drop_unused_columns).pipe(filter_by_time)

        save_csv(df, processed_file_path)

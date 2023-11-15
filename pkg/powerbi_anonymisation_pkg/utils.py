import pandas as pd


def month_avg(data):
    """
    >>> df = pd.DataFrame({'dteday': ['2021-09-29', '2021-09-28'], 'cnt': [1, 3], 'casual': [2, 4], 'registered': [3, 1]})  # noqa
    >>> month_avg(df)
          date  cnt  casual  registered
    0  2021-09  2.0     3.0         2.0
    """
    data = data.copy()
    cols = ["cnt", "casual", "registered"]
    data["date"] = pd.to_datetime(data["dteday"])
    data[cols] = data[cols].astype(int)
    period = data.date.dt.to_period("M")
    cnt_by_mnth = data.groupby(period)[cols].mean().reset_index()
    cnt_by_mnth["date"] = cnt_by_mnth["date"].astype(str)
    return cnt_by_mnth

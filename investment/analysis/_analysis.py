# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause


# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data
def analysis(df):
    close_price_series = df.loc[:,'Close']

    n_days_close_price_increase = n_days_close_price_decrease = n_days_close_price_the_same = 0
    amount_price_increase = amount_price_decrease = 0
    pct_price_increase = pct_price_decrease = 0

    total_days = len(close_price_series)
    print(f"total # days: {total_days}")

    for date_i in range(1, total_days):
        if close_price_series[date_i] > close_price_series[date_i-1]:
            n_days_close_price_increase += 1
            amount_price_increase += (close_price_series[date_i] - close_price_series[date_i-1])
            pct_price_increase += (close_price_series[date_i] - close_price_series[date_i-1]) / close_price_series[date_i-1]
        elif close_price_series[date_i] < close_price_series[date_i-1]:
            n_days_close_price_decrease += 1
            amount_price_decrease -= (close_price_series[date_i] - close_price_series[date_i-1])
            pct_price_decrease -= (close_price_series[date_i] - close_price_series[date_i-1]) / close_price_series[date_i-1]
        else:
            n_days_close_price_the_same += 1

    average_price_increase_per_day = amount_price_increase / n_days_close_price_increase
    average_price_decrease_per_day = amount_price_decrease / n_days_close_price_decrease
    average_pct_increase_per_day = 100 * pct_price_increase / n_days_close_price_increase
    average_pct_decrease_per_day = 100 * pct_price_decrease / n_days_close_price_decrease
    print(f"# days price increased: {n_days_close_price_increase}, # days price decreased: {n_days_close_price_decrease}, # days price stayed the same: {n_days_close_price_the_same}")
    print(f"average price increased during increase days per day: {average_price_increase_per_day:.3f} (avg +{average_pct_increase_per_day:.3f}%)")
    print(f"average price decreased during decrease days per day: {average_price_decrease_per_day:.3f} (avg -{average_pct_decrease_per_day:.3f}%)")


def demo():
    from ..data import demo_data
    df = demo_data()
    analysis(df)
    return df

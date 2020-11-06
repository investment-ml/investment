# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause

import yfinance as yf
import pandas as pd

import io
import pkgutil

import matplotlib.pyplot as plt

# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data
def pull_data(tickers='AAPL', start_date=None , end_date=None):
    """
    e.g., 
    start_date = '2020-01-01'
    end_date = '2020-09-28'
    """
    df = yf.download(tickers=tickers, start=start_date, end=end_date)
    return df

def demo_data():
    df = pd.read_csv(io.BytesIO(pkgutil.get_data(__name__, "data/yfinance/ticker=AAPL__from=19801212__to=20201105.csv")), header=0, encoding='utf8', sep=",")
    return df

def demo():
    data = demo_data()
    data[['Close', 'Adj Close']].plot()
    plt.show()

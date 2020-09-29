# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause

import yfinance as yf

# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data
def pull_data(ticker = 'AAPL', start_date = '2020-01-01', end_date = '2020-09-28'):
    """
    """
    data = yf.download(ticker, start_date, end_date)
    return data
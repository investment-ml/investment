# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
import os
import pickle
import shutil

# references:
# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data

def download_ticker_history_df(ticker: str = 'AAPL', verbose: bool = True):
    """
    e.g., 
    start_date = '2020-01-01'
    end_date = '2020-09-28'
    """
    yesterday = date.today() - timedelta(days=1)
    end_date_str = yesterday.strftime("%Y-%m-%d")
    if verbose:
        print(f"try to download [{ticker}] from yfinance")
    df = yf.download(tickers=ticker, start=None, end=end_date_str, auto_adjust = True, actions = True)
    df.reset_index(level=0, inplace=True) # convert Date from index to a column
    df['Date'] = df['Date'].astype(str)
    return df


def download_ticker_info_dict(ticker: str = 'AAPL'):
    info_dict = {}
    this_ticker = yf.Ticker(ticker)
    info_dict['info']                    = this_ticker.info
    info_dict['actions']                 = this_ticker.actions
    info_dict['dividends']               = this_ticker.dividends
    info_dict['splits']                  = this_ticker.splits
    info_dict['financials']              = this_ticker.financials
    info_dict['quarterly_financials']    = this_ticker.quarterly_financials
    info_dict['major_holders']           = this_ticker.major_holders
    info_dict['institutional_holders']   = this_ticker.institutional_holders
    info_dict['balance_sheet']           = this_ticker.balance_sheet
    info_dict['quarterly_balance_sheet'] = this_ticker.quarterly_balance_sheet
    info_dict['cashflow']                = this_ticker.cashflow
    info_dict['quarterly_cashflow']      = this_ticker.quarterly_cashflow
    info_dict['earnings']                = this_ticker.earnings
    info_dict['quarterly_earnings']      = this_ticker.quarterly_earnings
    info_dict['sustainability']          = this_ticker.sustainability
    info_dict['recommendations']         = this_ticker.recommendations
    info_dict['calendar']                = this_ticker.calendar
    info_dict['isin']                    = this_ticker.isin
    info_dict['options']                 = this_ticker.options
    info_dict['history']                 = pd.DataFrame()
    return info_dict


def get_ticker_data_dict(ticker: str = 'AAPL', force_redownload: bool = False):

    data_folder = os.path.dirname(__file__) + "/ticker_data/yfinance/"

    ticker_history_df_file = data_folder + ticker + "_history.csv"
    ticker_info_dict_file = data_folder + ticker + "_info_dict.pkl"

    if not os.path.isfile(ticker_history_df_file):

        try:
            ticker_history_df = download_ticker_history_df(ticker)
        except:
            raise SystemError("cannot download ticker history")

        try:
            ticker_info_dict = download_ticker_info_dict(ticker)
        except:
            raise SystemError("cannot download ticker info dict")

        ticker_history_df.to_csv(ticker_history_df_file, index=False)
        pickle.dump(ticker_info_dict, open(ticker_info_dict_file, "wb"))

    elif force_redownload:

        curr_df = pd.read_csv(ticker_history_df_file, index_col=False)
        try:
            new_df = download_ticker_history_df(ticker)
        except:
            raise SystemError("cannot download ticker history")

        curr_first_date_str = curr_df['Date'].iloc[0]
        curr_first_date = datetime.strptime(curr_first_date_str, "%Y-%m-%d").date()
        curr_last_date_str = curr_df['Date'].iloc[-1]
        curr_last_date = datetime.strptime(curr_last_date_str, "%Y-%m-%d").date()

        new_first_date_str = new_df['Date'].iloc[0]
        new_first_date = datetime.strptime(new_first_date_str, "%Y-%m-%d").date()
        new_last_date_str = new_df['Date'].iloc[-1]
        new_last_date = datetime.strptime(new_last_date_str, "%Y-%m-%d").date()

        # making sure the new df always has a wider date coverage
        if curr_df.shape[0] > new_df.shape[0]:
            raise ValueError(f"for ticker [{ticker}], the redownloaded df has fewer rows than the current one")
        elif (curr_first_date - new_first_date) < timedelta(days=0):
            raise ValueError(f"for ticker [{ticker}], the redownloaded df has a more recent start date: {new_first_date_str}, compared to the current one: {curr_first_date_str}")
        elif (curr_last_date - new_last_date) > timedelta(days=0):
            raise ValueError(f"for ticker [{ticker}], the redownloaded df has an older end date: {new_last_date_str}, compared to the current one: {curr_last_date_str}")
        else:
            try:
                ticker_info_dict = download_ticker_info_dict(ticker)
            except:
                raise SystemError("cannot download ticker info dict")
            shutil.copy2( ticker_history_df_file, data_folder + "backup" )
            shutil.copy2( ticker_info_dict_file,  data_folder + "backup" )
            new_df.to_csv(ticker_history_df_file, index=False)
            pickle.dump(ticker_info_dict, open(ticker_info_dict_file, "wb"))

    history_df = pd.read_csv(ticker_history_df_file, index_col=False)
    info_dict = pickle.load( open( ticker_info_dict_file, "rb" ) )
    info_dict['history'] = history_df
    return info_dict


def demo_data():
    data_dict = {}
    tickers = ['AAPL', 'AMZN', 'BRK-B', 'C', 'FB', 'GOOGL', 'MSFT', 'NFLX', 'OILU', 'TSLA', 'UDOW']
    for ticker in tickers:
        data_dict[ticker] = get_ticker_data_dict(ticker)
    return data_dict


def demo():
    data_dict = demo_data()
    for key in data_dict.keys():
        df = data_dict[key]
        df['history'][['Close']].plot()
        plt.show()

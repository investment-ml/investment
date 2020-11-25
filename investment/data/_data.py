# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: GNU General Public License v3 (GPLv3)

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
import os
from os.path import join
import pathlib
import pickle
import shutil

import warnings

# references:
# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data

def download_ticker_history_df(ticker: str = None, verbose: bool = True, download_today_data: bool = False):
    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if download_today_data:
        end_datetime = datetime.now() #- timedelta(days=0)
    else:
        end_datetime = datetime.now() - timedelta(days=1)
    
    ####################################################################################################
    if verbose:
        print(f"<--- Try to download [{ticker}] from yfinance, end_datetime: [{end_datetime}]")

    df = yf.download(tickers=ticker, start=None, end=end_datetime, auto_adjust=True, actions=True)

    if verbose:
        print('Download completed --->')
    ####################################################################################################

    df.reset_index(level=0, inplace=True) # convert Date from index to a column
    df['Date'] = df['Date'].astype(str)

    return df


def download_ticker_info_dict(ticker: str = None):

    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    info_dict = {}
    this_ticker = yf.Ticker(ticker)
    info_dict['info']                      = this_ticker.info
    info_dict['actions']                   = this_ticker.actions
    info_dict['dividends']                 = this_ticker.dividends
    info_dict['splits']                    = this_ticker.splits
    info_dict['financials']                = this_ticker.financials
    info_dict['quarterly_financials']      = this_ticker.quarterly_financials
    info_dict['major_holders']             = this_ticker.major_holders
    info_dict['institutional_holders']     = this_ticker.institutional_holders
    info_dict['balance_sheet']             = this_ticker.balance_sheet
    info_dict['quarterly_balance_sheet']   = this_ticker.quarterly_balance_sheet
    info_dict['cashflow']                  = this_ticker.cashflow
    info_dict['quarterly_cashflow']        = this_ticker.quarterly_cashflow
    info_dict['earnings']                  = this_ticker.earnings
    info_dict['quarterly_earnings']        = this_ticker.quarterly_earnings
    info_dict['sustainability']            = this_ticker.sustainability
    info_dict['recommendations']           = this_ticker.recommendations
    info_dict['calendar']                  = this_ticker.calendar
    info_dict['isin']                      = this_ticker.isin
    try:
        info_dict['options']               = this_ticker.options
    except:
        info_dict['options']               = None
    info_dict['history']                   = pd.DataFrame()
    return info_dict


def get_ticker_data_dict(ticker: str = None, verbose: bool = True, force_redownload: bool = False, download_today_data: bool = False, data_root_dir: str = None):

    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if data_root_dir is None:
        data_root_dir = join(str(pathlib.Path.home()), ".investment")
        #data_root_dir = os.path.dirname(__file__)
    
    data_dir = join(data_root_dir, "ticker_data/yfinance")
    data_backup_dir = join(data_dir, "backup")

    if not os.path.exists(data_dir):
        try:
            pathlib.Path(data_dir).mkdir(parents=True, exist_ok=True)
            #os.makedirs(data_dir)
        except:
            raise IOError(f"cannot create data dir: {data_dir}")

    if not os.path.exists(data_backup_dir):
        try:
            pathlib.Path(data_backup_dir).mkdir(parents=True, exist_ok=True)
            #os.makedirs(data_backup_dir)
        except:
            raise IOError(f"cannot create data backup dir: {data_backup_dir}")

    ticker_history_df_file = join(data_dir, f"{ticker}_history.csv")
    ticker_info_dict_file = join(data_dir, f"{ticker}_info_dict.pkl")

    if not os.path.isfile(ticker_history_df_file):

        try:
            ticker_history_df = download_ticker_history_df(ticker = ticker, verbose = verbose, download_today_data = download_today_data)
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
            new_df = download_ticker_history_df(ticker = ticker, verbose = verbose, download_today_data = download_today_data)
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
            #raise ValueError(f"for ticker [{ticker}], the redownloaded df has fewer rows than the current one")
            print(f"ticker: [{ticker}]")
            warnings.warn("the redownloaded df has fewer rows than the current one --> the current one will be used instead")
        elif (curr_first_date - new_first_date) < timedelta(days=0):
            #raise ValueError(f"for ticker [{ticker}], the redownloaded df has a more recent start date: {new_first_date_str}, compared to the current one: {curr_first_date_str}")
            print(f"ticker: [{ticker}]")
            warnings.warn("the redownloaded df has a more recent start date, compared to the current one --> the current one will be used instead")
        elif (curr_last_date - new_last_date) > timedelta(days=0):
            #raise ValueError(f"for ticker [{ticker}], the redownloaded df has an older end date: {new_last_date_str}, compared to the current one: {curr_last_date_str}")
            print(f"ticker: [{ticker}]")
            warnings.warn("the redownloaded df has an older end date, compared to the current one --> the current one will be used instead")
        else:
            try:
                ticker_info_dict = download_ticker_info_dict(ticker)
            except:
                raise SystemError("cannot download ticker info dict")
            shutil.copy2( ticker_history_df_file, data_backup_dir )
            shutil.copy2( ticker_info_dict_file,  data_backup_dir )
            new_df.to_csv(ticker_history_df_file, index=False)
            pickle.dump(ticker_info_dict, open(ticker_info_dict_file, "wb"))

    history_df = pd.read_csv(ticker_history_df_file, index_col=False)
    history_df = history_df[history_df['Volume']>0]
    history_df = history_df[history_df['Close']>0]
    history_df['Date'] = pd.to_datetime(history_df['Date'], format='%Y-%m-%d')
    info_dict = pickle.load( open( ticker_info_dict_file, "rb" ) )
    info_dict['history'] = history_df
    return info_dict


def demo_data():
    data_dict = {}
    tickers = list(set(['AAPL', 'AMZN', 'FB', 'GOOGL', 'MSFT', 'NFLX', 'TSLA']))
    for ticker in tickers:
        data_dict[ticker] = get_ticker_data_dict(ticker)
    return data_dict


def demo():
    data_dict = demo_data()
    for key in data_dict.keys():
        df = data_dict[key]
        df['history'][['Close']].plot()
        plt.show()

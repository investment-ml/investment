# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: GNU General Public License v3 (GPLv3)

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta, timezone
import os
from os.path import join
import pathlib
import pickle
import shutil

import warnings

from urllib.request import urlopen
from PyQt5.QtCore import QByteArray

import time


def datetime_to_tzinfo(x):
    return x.astimezone().tzinfo
    
def today_utc():
    t1 = datetime.today()
    return datetime(t1.year, t1.month, t1.day, tzinfo=timezone.utc)

def today_utc_timestamp():
    d1 = today_utc()
    return d1.timestamp()

# timestamp: seconds since epoch
def timestamp_to_datetime(x):
    return datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(seconds=x)

def datetime_to_timestamp(x):
    return x.timestamp()

# references:
# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data

def download_ticker_history_df(ticker: str = None, verbose: bool = True, download_today_data: bool = False, auto_retry: bool = False):
    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if download_today_data:
        end_datetime = datetime.now() #- timedelta(days=0)
    else:
        end_datetime = datetime.now() - timedelta(days=1)
    
    ####################################################################################################
    if verbose:
        print(f"\n<--- Try to download history of [{ticker}] from yfinance, end_datetime: [{end_datetime}]")

    successful_download = False
    while not successful_download:
        try:
            df = yf.download(tickers=ticker, start=None, end=end_datetime, auto_adjust=True, actions=True)
            successful_download = True
        except:
            successful_download = False
            if auto_retry:
                print(f"Download unsuccessful. ticker = {ticker}. Trying in 5 seconds: ", end='')
                for seconds in range(5,0,-1):
                    print(f"{seconds}...", end='')
                    time.sleep(1)
            else:
                print(f"Warning: Download unsuccessful. ticker = {ticker}. No auto retrying.")
                break

    if verbose:
        print('Download completed --->')
    ####################################################################################################

    df.reset_index(level=0, inplace=True) # convert Date from index to a column
    df['Date'] = df['Date'].astype(str)

    return df


def download_ticker_info_dict(ticker: str = None, verbose: bool = True, auto_retry: bool = False):

    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    info_dict = {}
    this_ticker = yf.Ticker(ticker)

    if verbose:
        print(f"\n<--- Try to download info of [{ticker}] from yfinance")

    ####################################################################

    successful_download = False
    while not successful_download:
        try:
            info_dict['info']                      = this_ticker.info

            info_dict['info']['logo'] = None
            if 'logo_url' in info_dict['info'].keys():
                if info_dict['info']['logo_url'] is not None:
                    try:
                        page = urlopen(info_dict['info']['logo_url'])
                        info_dict['info']['logo'] = QByteArray(page.read())
                    except:
                        pass

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

            successful_download = True

        except:
            successful_download = False
            if auto_retry:
                print(f"Download unsuccessful. ticker = {ticker}. Trying in 5 seconds: ", end='')
                for seconds in range(5,0,-1):
                    print(f"{seconds}...", end='')
                    time.sleep(1)
            else:
                print(f"Warning: Download unsuccessful. ticker = {ticker}. No auto retrying.")
                break

    ####################################################################

    if verbose:
        print('Download completed --->')

    info_dict['data_download_time']        = datetime.now()
    info_dict['history']                   = pd.DataFrame()
    return info_dict


def get_ticker_data_dict(ticker: str = None, verbose: bool = True, force_redownload: bool = False, download_today_data: bool = False, data_root_dir: str = None, auto_retry: bool = False):

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
            ticker_history_df = download_ticker_history_df(ticker = ticker, verbose = verbose, download_today_data = download_today_data, auto_retry = auto_retry)
        except:
            raise SystemError("cannot download ticker history")

        try:
            ticker_info_dict = download_ticker_info_dict(ticker, verbose = verbose, auto_retry = auto_retry)
        except:
            raise SystemError("cannot download ticker info dict")

        ticker_history_df.to_csv(ticker_history_df_file, index=False)
        pickle.dump(ticker_info_dict, open(ticker_info_dict_file, "wb"))

    elif force_redownload:

        curr_df = pd.read_csv(ticker_history_df_file, index_col=False)
        try:
            new_df = download_ticker_history_df(ticker = ticker, verbose = verbose, download_today_data = download_today_data, auto_retry = auto_retry)
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
                ticker_info_dict = download_ticker_info_dict(ticker, verbose = verbose, auto_retry = auto_retry)
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


def get_formatted_ticker_data(ticker_data_dict, use_html: bool = False):

    if not 'info' in ticker_data_dict.keys():
        if use_html:
            formatted_str = f"<body style=\"font-family:Courier New;\">the key 'info' does not exist in ticker_data_dict</body>"
        else:
            formatted_str = f"the key 'info' does not exist in ticker_data_dict"

        return formatted_str

    ticker_info = ticker_data_dict['info']
    ticker_info_keys = ticker_info.keys()

    # long name
    if use_html:
        ticker_long_name = f"<b>{ticker_info['longName']}</b>"
    else:
        ticker_long_name = f"{ticker_info['longName']}"

    # sector info
    if use_html:
        sector_info = f"<br/><br/>Sector info unavailable"
    else:
        sector_info = f"\n\nSector info unavailable"
    if 'sector' in ticker_info_keys:
        if use_html:
            sector_info = f"<br/><br/>Sector: [{ticker_info['sector']}]"
        else:
            sector_info = f"\n\nSector: [{ticker_info['sector']}]"
        if 'industry' in ticker_info_keys:
            sector_info += f", Industry: [{ticker_info['industry']}]"

    # earnings
    if use_html:
        earnings_info = f"<br/><br/>Earnings info unavailable"
    else:
        earnings_info = f"\n\nEarnings info unavailable"
    if 'trailingEps' in ticker_info_keys:
        trailingEps = ticker_info['trailingEps']
        if trailingEps is not None:
            if use_html:
                earnings_info = f"<br/><br/>Earnings per share (EPS) from the last four quarters: ${trailingEps:.2f}"
            else:
                earnings_info = f"\n\nEarnings per share (EPS) from the last four quarters: ${trailingEps:.2f}"
            if 'forwardEps' in ticker_info_keys:
                forwardEps = ticker_info['forwardEps']
                if forwardEps is not None:
                    EPS_change_pct = 100*(forwardEps - trailingEps)/abs(trailingEps)
                    if use_html:
                        earnings_info += f"<br/>EPS estimated for the next four quarters: ${forwardEps:.2f}, which is <b><span style=\"color:blue;\">{round(EPS_change_pct,2):+.2f}%</span></b>"
                    else:
                        earnings_info += f"\nEPS estimated for the next four quarters: ${forwardEps:.2f}, which is {round(EPS_change_pct,2):+.2f}%"

    # profitability
    if use_html:
        profitability_info = f"<br/><br/>Profitability info unavailable"
    else:
        profitability_info = f"\n\nProfitability info unavailable"
    if 'profitMargins' in ticker_info_keys:
        profitMargins = ticker_info['profitMargins']
        if profitMargins is not None:
            if use_html:
                profitability_info = f"<br/><br/>The business has generated {profitMargins*100:.2f}% profit out of each dollar of sale"
            else:
                profitability_info = f"\n\nThe business has generated {profitMargins*100:.2f}% profit out of each dollar of sale"

    # institutions
    if use_html:
        institutions_holding_info = f"<br/><br/>Institution holding info unavailable"
    else:
        institutions_holding_info = f"\n\nInstitution holding info unavailable"   
    if 'heldPercentInstitutions' in ticker_info_keys:
        percent_held_by_institutions = ticker_info['heldPercentInstitutions']
        if percent_held_by_institutions is not None:
            if use_html:
                institutions_holding_info = f"<br/><br/>Shares held by institutions: {100*percent_held_by_institutions:.2f}%"
            else:
                institutions_holding_info = f"\n\nShares held by institutions: {100*percent_held_by_institutions:.2f}%"
            if 'institutional_holders' in ticker_data_dict.keys():
                institutional_holders_df = ticker_data_dict['institutional_holders']
                if institutional_holders_df is not None:
                    if all(elem in institutional_holders_df.columns for elem in ['% Out','Value']):
                        tmp_df = institutional_holders_df.drop(['% Out','Value'], axis=1, inplace=False) # axis: 0=row, 1=col
                        if 'sharesOutstanding' in ticker_info_keys:
                            sharesOutstanding = ticker_info['sharesOutstanding']
                            if sharesOutstanding is not None:
                                tmp_df['% Out'] = tmp_df['Shares'].apply(lambda x: f"{x/sharesOutstanding * 100:.2f}%")
                        if use_html:
                            institutions_holding_info += f"<br/><br/>Institutional Holders:{tmp_df.to_html(index=False)}"
                        else:
                            institutions_holding_info += f"\n\nInstitutional Holders:\n{tmp_df.to_string(index=False)}"

    # dividends
    if use_html:
        dividends_info = f"<br/><br/>Dividends info unavailable"
    else:
        dividends_info = f"\n\nDividends info unavailable"
    if ticker_data_dict['dividends'] is not None:
        dividends_df = ticker_data_dict['dividends'].reset_index(level=0)
        if len(dividends_df) == 0:
            if use_html:
                dividends_info = "<br/><br/>Dividends info never reported"
            else:
                dividends_info = "\n\nDividends info never reported"
        else:
            if use_html:
                dividends_info = f"<br/><br/>Most recent 10 reported dividends:"
                dividends_info_df = pd.DataFrame()
            else:
                dividends_info = f"\n\nMost recent 10 reported dividends:\nDate\tDividends\tYield %"
            date_close_df = ticker_data_dict['history'][['Date','Close']]
            for idx, row in dividends_df.tail(10).iterrows():
                try:
                    close_price_on_this_date = float(date_close_df[date_close_df.Date == row['Date']].Close)
                    dividends_yield_percent = f"{100*row['Dividends']/close_price_on_this_date:.2f}%"
                except:
                    dividends_yield_percent = "NA"
                if use_html:
                    dividends_info_df = dividends_info_df.append({'Date': row['Date'].date(), 'Dividends': f"${row['Dividends']:.2f}", 'Yield %': dividends_yield_percent}, ignore_index = True)
                else:
                    dividends_info += f"\n{row['Date'].date()}\t${row['Dividends']:.2f}\t{dividends_yield_percent}"
            if use_html:
                dividends_info += dividends_info_df.to_html(index=False)

    # measures
    if use_html:
        risk_info = f"<br/><br/>Beta measure unavailable"
    else:
        risk_info = f"\n\nBeta measure unavailable"
    # beta: covariance of stock with market
    if 'beta' in ticker_info_keys:
        beta = ticker_info['beta']
        if beta is not None:
            if use_html:
                risk_info = f"<br/><br/>Beta: {beta:.2f}"
            else:
                risk_info = f"\n\nBeta: {beta:.2f}"
            if beta > 1.00:
                risk_info += f" (more volatile than the overall market)"
            if beta <= 1.00:
                risk_info += f" (less volatile than the overall market)"

    # summary
    if 'longBusinessSummary' in ticker_info_keys:
        if use_html:
            long_business_summary = f"<br/><br/>{ticker_info['longBusinessSummary']}"
        else:
            long_business_summary = f"\n\n{ticker_info['longBusinessSummary']}"
    else:
        long_business_summary = ""

    # logo
    logo = ""
    if 'logo' in ticker_info_keys:
        if ticker_info['logo'] is not None:
            logo_base64 = ticker_info['logo'].toBase64()
            if logo_base64 is not None:
                if use_html:
                    logo = f"<br/><br/>Logo:<br/><img src=\"data:image/png;base64,{str(logo_base64,'utf-8')}\">"
                else:
                    if 'logo_url' in ticker_info_keys:
                        logo = f"\n\nLogo: {ticker_info['logo_url']}"

    if use_html:
        formatted_str = f"<body style=\"font-family:Courier New;\">{ticker_long_name}{sector_info}{earnings_info}{profitability_info}{institutions_holding_info}{dividends_info}{risk_info}{long_business_summary}{logo}</body>"  
    else:
        formatted_str = f"{ticker_long_name}{sector_info}{earnings_info}{profitability_info}{institutions_holding_info}{dividends_info}{risk_info}{long_business_summary}{logo}"  
    
    return formatted_str


def test_data():
    data_dict = {}
    tickers = list(set(['AAPL', 'AMZN', 'FB', 'GOOGL', 'MSFT', 'NFLX', 'TSLA']))
    for ticker in tickers:
        data_dict[ticker] = get_ticker_data_dict(ticker)
    return data_dict


def test():
    data_dict = test_data()
    for key in data_dict.keys():
        print("\n<-------------------------------------------------------------------------------------------")
        df = data_dict[key]
        df['history'][['Close']].plot()
        plt.show()
        print(get_formatted_ticker_data(df))
        print("------------------------------------------------------------------------------------------->\n")

    d1 = datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(seconds=1604620800)
    assert timestamp_to_datetime(datetime_to_timestamp(d1)) == d1, "unequal datetime"

    t_list = [1604620800, today_utc_timestamp()]
    for t in t_list:
        assert datetime_to_timestamp(timestamp_to_datetime(t)) == t, "unequal timestamp"

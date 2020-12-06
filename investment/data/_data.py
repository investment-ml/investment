# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL

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

from urllib.request import urlopen
from PyQt5.QtCore import QByteArray

import time

from ._ticker import Ticker

from functools import total_ordering

@total_ordering
class timedata(object):
    def __init__(self, time_stamp: float=None, date_time=None, Y_m_d={}):
        """
        time_stamp: seconds since epoch
        date_time: datetime_object_with_tzinfo
        Y_m_d: {'year': 2020, 'month': 11, 'day': 15}, or (2020, 11, 15)

        internally, self._datetime and self._timestamp are stored in UTC
        """
        if time_stamp is None and date_time is None:
            if Y_m_d == {} or Y_m_d == ():
                raise ValueError("either timestamp, datetime, or Y_m_d must be specified")
            elif type(Y_m_d) == dict:
               self.datetime = datetime(Y_m_d['year'], Y_m_d['month'], Y_m_d['day'], tzinfo=timezone.utc)
            elif type(Y_m_d) == tuple:
               self.datetime = datetime(Y_m_d[0], Y_m_d[1], Y_m_d[2], tzinfo=timezone.utc) 
        else:
            if time_stamp is None:
                self.datetime = date_time
            else:
                self.timestamp = time_stamp
                
    @property
    def datetime(self):
        return self._datetime

    @datetime.setter
    def datetime(self, datetime_object_with_tzinfo):
        self._datetime = datetime_object_with_tzinfo.astimezone(tz=timezone.utc)
        self._timestamp = self._datetime.timestamp()
        assert datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(seconds=self._timestamp) == self._datetime, "unequal datetime in datetime.setter()"

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, seconds_since_epoch):
        self._timestamp = seconds_since_epoch
        self._datetime = datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(seconds=self._timestamp)
        assert self._datetime.timestamp() == self._timestamp, "unequal timestamp in timestamp.setter()"

    def __sub__(self, other):
        type_of_other = type(other)
        if type_of_other == timedelta:
            return (self.datetime - other)
        elif type_of_other == int:
            return (self.timestamp - other) # assuming it's seconds
        elif type_of_other == type(self):
            return (self.timestamp - other.timestamp) # difference in seconds
        elif type_of_other == datetime:
            return (self.timestamp - timedata(date_time=other).timestamp) # difference in seconds
        else:
            return NotImplemented

    def __eq__(self, other):
        type_of_other = type(other)
        if type_of_other == datetime:
            return (self.datetime == timedata(date_time=other).datetime)
        elif type_of_other == int:
            return (self.timestamp == other)
        elif type_of_other == type(self):
            return (self.datetime == other.datetime)
        else:
            return NotImplemented

    def __lt__(self, other):
        type_of_other = type(other)
        if type_of_other == datetime:
            return (self.datetime < timedata(date_time=other).datetime)
        elif type_of_other == int:
            return (self.timestamp < other)
        elif type_of_other == type(self):
            return (self.datetime < other.datetime)
        else:
            return NotImplemented

    #def datetime_to_tzinfo(self):
    #    return self.datetime.astimezone().tzinfo


def rmse(pred, target):
    return np.sqrt(np.mean((pred-target)**2))

def gradient_test():
    x = np.linspace(1, 20, int(1e6))
    #dx = np.gradient(x, edge_order=2)
    f = np.exp(x)
    grad = np.gradient(f, x, edge_order=2)
    print(f"RMSE: {rmse(f, grad)}, max diff. = {np.abs(f-grad).max()}")

# references:
# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data

def download_ticker_history_df(ticker: str = None, verbose: bool = True, download_today_data: bool = False, auto_retry: bool = False):
    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if download_today_data:
        end_datetime = datetime.now(tz=timezone.utc) #- timedelta(days=0)
    else:
        end_datetime = datetime.now(tz=timezone.utc) - timedelta(days=1)
    
    ####################################################################################################
    if verbose:
        print(f"\n<--- Try to download history of [{ticker}] from yfinance, end_datetime: [{end_datetime}]")

    successful_download = False
    retry_times = 5
    while not successful_download and retry_times>=0:
        try:
            df = yf.download(tickers=ticker, start=None, end=end_datetime, auto_adjust=True, actions=True)
            successful_download = True
        except:
            successful_download = False
            retry_times -= 1
            if auto_retry:
                print(f"Download unsuccessful. ticker = {ticker}. Trying in 5 seconds: ", end='')
                for seconds in range(5,0,-1):
                    print(f"{seconds}...", end='')
                    time.sleep(1)
            else:
                print(f"Warning: Download unsuccessful. ticker = {ticker}. No auto retrying.")
                break

    if verbose:
        if successful_download == False and retry_times<0:
            print('Max. retry times reached. Unsuccessful download. Download aborted --->')
        else:
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
    retry_times = 5
    while not successful_download and retry_times>=0:
        try:
            try:
                info_dict['info']                      = this_ticker.info
            except:
                info_dict['info'] = None

            info_dict['info']['logo'] = None
            if 'logo_url' in info_dict['info'].keys():
                if info_dict['info']['logo_url'] is not None:
                    try:
                        page = urlopen(info_dict['info']['logo_url'])
                        info_dict['info']['logo'] = QByteArray(page.read())
                    except:
                        pass

            if not 'sector' in info_dict['info'].keys():
                info_dict['info']['sector'] = None

            if not 'industry' in info_dict['info'].keys():
                info_dict['info']['industry'] = None    
                
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
            retry_times -= 1
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
        if successful_download == False and retry_times<0:
            print('Max. retry times reached. Unsuccessful download. Download aborted --->')
        else:
            print('Download completed --->')

    info_dict['data_download_time']        = datetime.now(timezone.utc)
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

    if (not os.path.isfile(ticker_history_df_file)) or (not os.path.isfile(ticker_info_dict_file)):

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
            print("*** The redownloaded df has fewer rows than the current one --> the current one will be used instead")
        elif (curr_first_date - new_first_date) < timedelta(days=0):
            #raise ValueError(f"for ticker [{ticker}], the redownloaded df has a more recent start date: {new_first_date_str}, compared to the current one: {curr_first_date_str}")
            print(f"ticker: [{ticker}]")
            print("*** The redownloaded df has a more recent start date, compared to the current one --> the current one will be used instead")
        elif (curr_last_date - new_last_date) > timedelta(days=0):
            #raise ValueError(f"for ticker [{ticker}], the redownloaded df has an older end date: {new_last_date_str}, compared to the current one: {curr_last_date_str}")
            print(f"ticker: [{ticker}]")
            print("*** The redownloaded df has an older end date, compared to the current one --> the current one will be used instead")
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
    history_df = history_df[(history_df['Volume']>0) & (history_df['Close']>0)]
    history_df['Date'] = pd.to_datetime(history_df['Date'], format='%Y-%m-%d', utc=True) # "utc=True" is to be consistent with yfinance datetimes, which are received as UTC.
    info_dict = pickle.load( open( ticker_info_dict_file, "rb" ) )
    if 'info' not in info_dict.keys():
        raise KeyError(f"for ticker = [{ticker}], 'info' is not in the info_dict keys")
    info_dict['history'] = history_df
    info_dict['ticker'] = ticker
    return info_dict


def get_formatted_ticker_data(ticker_data_dict, use_html: bool = False):

    if use_html:
        formatted_str = f"<body style=\"font-family:Courier New;\">the key 'info' does not exist in ticker_data_dict</body>"
    else:
        formatted_str = f"the key 'info' does not exist in ticker_data_dict"

    if not 'info' in ticker_data_dict.keys():
        return formatted_str

    ticker_info = ticker_data_dict['info']
    if ticker_info is None:
        return formatted_str

    ticker_info_keys = ticker_info.keys()

    # long name
    if use_html:
        ticker_long_name = f"<b>{ticker_info['longName']}</b>"
    else:
        ticker_long_name = f"{ticker_info['longName']}"

    # sector info
    if use_html:
        sector_info = f"<br/><hr>Sector info unavailable"
    else:
        sector_info = f"\n\nSector info unavailable"
    if 'sector' in ticker_info_keys:
        if use_html:
            sector_info = f"<br/><hr>Sector: [{ticker_info['sector']}]"
        else:
            sector_info = f"\n\nSector: [{ticker_info['sector']}]"
        if 'industry' in ticker_info_keys:
            sector_info += f", Industry: [{ticker_info['industry']}]"

    # earnings
    this_ticker = Ticker(ticker_data_dict=ticker_data_dict)
    if use_html:
        earnings_info = f"<br/><hr>Earnings info unavailable"
    else:
        earnings_info = f"\n\nEarnings info unavailable"
    if this_ticker.trailingEps is not None:
        if use_html:
            earnings_info = f"<br/><hr>Earnings per share (EPS) from the last four quarters: ${this_ticker.trailingEps:.2f}"
        else:
            earnings_info = f"\n\nEarnings per share (EPS) from the last four quarters: ${this_ticker.trailingEps:.2f}"
        if this_ticker.forwardEps is not None:
            if use_html:
                earnings_info += f"<br/>EPS estimated for the next four quarters: ${this_ticker.forwardEps:.2f}, which is <b><span style=\"color:blue;\">{round(this_ticker.Eps_change_pct,2):+.2f}%</span></b>"
            else:
                earnings_info += f"\nEPS estimated for the next four quarters: ${this_ticker.forwardEps:.2f}, which is {round(this_ticker.Eps_change_pct,2):+.2f}%"
        if this_ticker.Eps_growth_rate is not None:
            if use_html:
                earnings_info += f"<br/><br/>The 5-yr EPS growth rate is estimated to be <b><span style=\"color:blue;\">{this_ticker.Eps_growth_rate:+.2f}%</span></b> (compound rate per year)"
            else:
                earnings_info += f"\n\nThe 5-yr EPS growth rate is estimated to be {this_ticker.Eps_growth_rate:+.2f}% (compound rate per year)"
    
    # apples-to-apples comparison
    # e.g., https://www.investopedia.com/terms/p/price-earningsratio.asp#investor-expectations
    if use_html:
        company_to_company_comparison_info = f"<br/><hr>Company-to-company comparison info unavailable"
    else:
        company_to_company_comparison_info = f"\n\nCompany-to-company comparison info unavailable"
    if this_ticker.trailingPE is not None:
        if use_html:
            company_to_company_comparison_info = f"<br/><hr>For an apples-to-apples comparison, the ratio of current price to the earnings from the last four quarters (the trailing P/E, <b>the earnings multiple</b>): <b><span style=\"color:blue;\">{this_ticker.trailingPE:.2f}</span></b><br/><br/>A high P/E ratio could mean that an over-valued stock, or high expectation of growth rates in the future. Traditionally the P/E could be between 6 and 120, with a long-term mean of 15."
        else:
            company_to_company_comparison_info = f"\n\nFor an apples-to-apples comparison, the ratio of current price to the earnings from the last four quarters (the trailing P/E, the earnings multiple): {this_ticker.trailingPE:.2f} A high P/E ratio could mean that an over-valued stock, or high expectation of growth rates in the future. Traditionally the P/E could be between 6 and 120, with a long-term mean of 15."
        if this_ticker.forwardPE is not None:
            if use_html:
                company_to_company_comparison_info += f"<br/><br/>The ratio of current price to the earnings estimated for the next four quarters (the forward P/E, <b>the earnings multiple</b>): <b><span style=\"color:blue;\">{this_ticker.forwardPE:.2f}</span></b>. If the forward P/E ratio is lower (or higher) than the trailing P/E ratio, it means analysts are expecting earnings to increase (or decrease)."
            else:
                company_to_company_comparison_info += f"\n\nThe ratio of current price to the earnings estimated for the next four quarters (the forward P/E, the earnings multiple): {this_ticker.forwardPE:.2f}. If the forward P/E ratio is lower (or higher) than the trailing P/E ratio, it means analysts are expecting earnings to increase (or decrease)."
    if this_ticker.PEG_ratio is not None:
        if use_html:
            company_to_company_comparison_info += f"<br/><br/>The Price/Earnings-to-Growth (PEG) ratio is <b><span style=\"color:blue;\">{this_ticker.PEG_ratio}</span></b> (which is over-valued if &gt; 1.0, or under-valued if &lt; 1.0; in theory, the lower the PEG ratio the better, which implies paying less for future earnings growth.)"
        else:
            company_to_company_comparison_info += f"\n\nThe Price/Earnings-to-Growth (PEG) ratio is {this_ticker.PEG_ratio} (which is over-valued if > 1.0, or under-valued if < 1.0; in theory, the lower the PEG ratio the better, which implies paying less for future earnings growth.)"

    # profitability
    if use_html:
        profitability_info = f"<br/><hr>Profitability info unavailable"
    else:
        profitability_info = f"\n\nProfitability info unavailable"
    if 'profitMargins' in ticker_info_keys:
        profitMargins = ticker_info['profitMargins']
        if profitMargins is not None:
            if use_html:
                profitability_info = f"<br/><hr>The business has generated {profitMargins*100:.2f}% profit out of each dollar of sale"
            else:
                profitability_info = f"\n\nThe business has generated {profitMargins*100:.2f}% profit out of each dollar of sale"

    # valuation analysis
    # https://www.investopedia.com/terms/m/multiple.asp
    if use_html:
        valuation_info = f"<br/><hr>Valuation info unavailable"
    else:
        valuation_info = f"/n/nValuation info unavailable"
    # method1: cash flow (intrinsic valuation)
    # method2: multiple of performance (relative valuation)
    if this_ticker.EV_to_EBITDA is not None:
        if use_html:
            valuation_info = f"<br/><hr>Valuation info. How much to buy a company? The firm's total value to its earnings before interest, taxes, depreciation, and amortization: <b><span style=\"color:blue;\">{this_ticker.EV_to_EBITDA:.2f}</span></b> (tends to be between 11-14, while below 10 is considered healthy; the lower, the better)"
        else:
            valuation_info = f"\n\nValuation info. How much to buy a company? The firm's total value to its earnings before interest, taxes, depreciation, and amortization: {this_ticker.EV_to_EBITDA:.2f} (which tends to be between 11-14, while below 10 is considered healthy; the lower, the better)"

    # institutions
    if use_html:
        institutions_holding_info = f"<br/><hr>Institution holding info unavailable"
    else:
        institutions_holding_info = f"\n\nInstitution holding info unavailable"   
    if 'heldPercentInstitutions' in ticker_info_keys:
        percent_held_by_institutions = ticker_info['heldPercentInstitutions']
        if percent_held_by_institutions is not None:
            if use_html:
                institutions_holding_info = f"<br/><hr>Shares held by institutions: {100*percent_held_by_institutions:.2f}%"
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
        dividends_info = f"<br/><hr>Dividends info unavailable"
    else:
        dividends_info = f"\n\nDividends info unavailable"
    if ticker_data_dict['dividends'] is not None:
        dividends_df = ticker_data_dict['dividends'].reset_index(level=0)
        if len(dividends_df) == 0:
            if use_html:
                dividends_info = "<br/><hr>Dividends info never reported"
            else:
                dividends_info = "\n\nDividends info never reported"
        else:
            dividends_df['Date'] = pd.to_datetime(dividends_df['Date'], format='%Y-%m-%d', utc=True)
            if use_html:
                dividends_info = f"<br/><hr>Most recent 10 reported dividends:"
                dividends_info_df = pd.DataFrame()
            else:
                dividends_info = f"\n\nMost recent 10 reported dividends:\nDate\tDividends\tapprox. Yield %"
            date_close_df = ticker_data_dict['history'][['Date','Close']]
            for idx, row in dividends_df.tail(10).iterrows():
                try:
                    close_price_on_this_date = float(date_close_df[date_close_df.Date == row['Date']].Close)
                    dividends_yield_percent = f"{100*row['Dividends']/close_price_on_this_date:.2f}%"
                except:
                    dividends_yield_percent = "NA"
                if use_html:
                    dividends_info_df = dividends_info_df.append({'Date': row['Date'].date(), 'Dividends': f"${row['Dividends']:.2f}", 'approx. Yield %': dividends_yield_percent}, ignore_index = True)
                else:
                    dividends_info += f"\n{row['Date'].date()}\t${row['Dividends']:.2f}\t{dividends_yield_percent}"
            if use_html:
                dividends_info += dividends_info_df.to_html(index=False)

    # measures
    if use_html:
        risk_info = f"<br/><hr>Beta measure unavailable"
    else:
        risk_info = f"\n\nBeta measure unavailable"
    # beta: covariance of stock with market
    if 'beta' in ticker_info_keys:
        beta = ticker_info['beta']
        if beta is not None:
            if use_html:
                risk_info = f"<br/><hr>Beta: {beta:.2f}"
            else:
                risk_info = f"\n\nBeta: {beta:.2f}"
            if beta > 1.00:
                risk_info += f" (more volatile than the overall market)"
            if beta <= 1.00:
                risk_info += f" (less volatile than the overall market)"

    # summary
    if 'longBusinessSummary' in ticker_info_keys:
        if use_html:
            long_business_summary = f"<br/><hr>{ticker_info['longBusinessSummary']}"
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
                    logo = f"<br/><hr>Logo:<br/><img src=\"data:image/png;base64,{str(logo_base64,'utf-8')}\">"
                else:
                    if 'logo_url' in ticker_info_keys:
                        logo = f"\n\nLogo: {ticker_info['logo_url']}"

    if use_html:
        formatted_str = f"<body style=\"font-family:Courier New;\">{ticker_long_name}{sector_info}{earnings_info}{company_to_company_comparison_info}{profitability_info}{valuation_info}{institutions_holding_info}{dividends_info}{risk_info}{long_business_summary}{logo}</body>"  
    else:
        formatted_str = f"{ticker_long_name}{sector_info}{earnings_info}{company_to_company_comparison_info}{profitability_info}{valuation_info}{institutions_holding_info}{dividends_info}{risk_info}{long_business_summary}{logo}"  
    
    return formatted_str


def test_data(ticker_only: bool = False):
    data_dict = {}
    tickers = list(set(['AAPL', 'AMZN', 'BRK-B', 'FB', 'GOOGL', 'MSFT', 'NFLX', 'TSLA']))
    if ticker_only:
        return tickers
    else:
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

    t_list = [timedata(time_stamp=1604620800), timedata(date_time=datetime.today()), timedata(Y_m_d={'year': 2020, 'month': 3, 'day': 27})]
    for t in t_list:
        print(f"timestamp = {t.timestamp}, datetime = {t.datetime}")

    gradient_test()

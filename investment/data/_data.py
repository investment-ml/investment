# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta, timezone
import pathlib
import pickle
import shutil

from urllib.request import urlopen
import base64

import time

from functools import total_ordering

import numpy as np

# Treasury (U.S. Government Bills, Notes, Bonds, and TIPS) Yield 10 Years
# Treasury Yield is the return on investment, expressed as a percentage, on the U.S. government's debt obligations.
try:
    risk_free_interest_rate = yf.Ticker('^TNX').history(period='1d').iloc[0]['Close'] # e.g., 1.64
except:
    risk_free_interest_rate = 1.64
# reference: London Inter-Bank Offered Rate (LIBOR)
# https://www.theice.com/iba/usd-rates

# Tresury Yield is different from the Federal funds rate
# The Federal funds rate is the interest rate at which depository institutions lend reserve balances to other depository institutions overnight.

@total_ordering
class timedata(object):
    def __init__(self, time_stamp: float=None, date_time=None, Y_m_d_str: str = None, Y_m_d={}, days_from_now=0, use_y_m_d_precision=False):
        """
        time_stamp: seconds since epoch
        date_time: datetime_object_with_tzinfo
        Y_m_d: {'year': 2020, 'month': 11, 'day': 15}
        Y_m_d_str: '2020-11-15'
        Y_m_d_tuple: (2020, 11, 15)

        internally, self._datetime and self._timestamp are stored in UTC
        """
        if time_stamp is None and date_time is None:
            if Y_m_d_str is not None:
                Y_m_d = {'year': int(Y_m_d_str[0:4]), 'month': int(Y_m_d_str[5:7]), 'day': int(Y_m_d_str[8:10])}
            if Y_m_d == {} or Y_m_d == ():
                if use_y_m_d_precision:
                    this_now = datetime.now(tz=timezone.utc)
                    self.datetime = datetime(this_now.year, this_now.month, this_now.day, tzinfo=timezone.utc) + timedelta(days=days_from_now)
                else:
                    self.datetime = datetime.now(tz=timezone.utc) + timedelta(days=days_from_now)
                #raise ValueError("either time_stamp, date_time, or Y_m_d must be specified")
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
    def yymmdd_str(self):
        return f"{self.datetime.strftime('%y')}{self.datetime.strftime('%m')}{self.datetime.strftime('%d')}"

    @property
    def Y_m_d_str(self):
        return self.datetime.strftime('%Y-%m-%d')

    @property
    def Y_m_d(self):
        return {'year': self.datetime.strftime('%Y'), 'month': self.datetime.strftime('%m'), 'day': self.datetime.strftime('%d')}

    @property
    def Y_m_d_tuple(self):
        return (int(self.datetime.strftime('%Y')), int(self.datetime.strftime('%m')), int(self.datetime.strftime('%d')))

    @property
    def remaining_days_this_year(self):
        return (timedata(Y_m_d = {'year': self.datetime.year, 'month': 12, 'day': 31}).datetime - self.datetime).days + 1

    @property
    def now(self):
        self._datetime = datetime.now(tz=timezone.utc)
        self._timestamp = self._datetime.timestamp()
        return self

    @property
    def date(self):
        return self._datetime.date()

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
        assert round(self._datetime.timestamp(),6) == round(self._timestamp,6), "unequal timestamp in timestamp.setter()"

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

###########################################################################################

def rmse(pred, target):
    return np.sqrt(np.mean((pred-target)**2))

def gradient_test():
    x = np.linspace(1, 20, int(1e6))
    #dx = np.gradient(x, edge_order=2)
    f = np.exp(x)
    grad = np.gradient(f, x, edge_order=2)
    print(f"RMSE: {rmse(f, grad)}, max diff. = {np.abs(f-grad).max()}")

###########################################################################################

# references:
# https://www.quora.com/Using-Python-whats-the-best-way-to-get-stock-data

def download_ticker_history_df(ticker: str = None, verbose: bool = True, download_today_data: bool = False, auto_retry: bool = False):
    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if download_today_data:
        end_datetime = timedata().now.datetime #- timedelta(days=0)
    else:
        end_datetime = timedata().now.datetime - timedelta(days=1)
    
    ####################################################################################################
    if verbose:
        print(f"\n<--- Try to download history of [{ticker}] from yfinance, end_datetime: [{end_datetime}]")

    successful_download = False
    retry_times = 5
    while not successful_download and retry_times>=0:
        try:
            df = yf.download(tickers=ticker, start=None, end=end_datetime, auto_adjust=True, actions=True)
            df.drop_duplicates(inplace = True)
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


def download_ticker_info_dict(ticker: str = None, verbose: bool = True, auto_retry: bool = False, web_scraper = None, download_short_interest: bool = False):

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
                info_dict['info'] = this_ticker.info
            except:
                info_dict['info'] = None

            info_dict['info']['logo'] = None
            if 'logo_url' in info_dict['info'].keys():
                if info_dict['info']['logo_url'] is not None:
                    try:
                        page = urlopen(info_dict['info']['logo_url'])
                        info_dict['info']['logo'] = bytearray(page.read())
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
                info_dict['options']               = this_ticker.options # expiration dates
                info_dict['option_chain_dict']     = {}
                for this_expiration_date in this_ticker.options:
                    opt = this_ticker.option_chain(this_expiration_date)
                    opt_calls = opt.calls
                    opt_puts = opt.puts
                    opt_calls['type'] = 'calls'
                    opt_puts['type'] = 'puts'
                    opt_combined = pd.concat([opt_calls, opt_puts], axis=0)
                    info_dict['option_chain_dict'][this_expiration_date] = opt_combined
            except:
                info_dict['options']               = None
                info_dict['option_chain_dict']     = {}

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

    info_dict['data_download_time']    = datetime.now(timezone.utc)
    info_dict['history']               = pd.DataFrame()

    ####################################################################

    from ._ticker import ticker_group_dict, tickers_with_no_volume, tickers_with_no_PT

    if web_scraper is not None:
        if (ticker not in tickers_with_no_volume) and (ticker not in ticker_group_dict['ETF database']) and (ticker not in tickers_with_no_PT) and (ticker[0] != '^'):
            info_dict['price_target'] = web_scraper().price_target(ticker=ticker)
        else:
            info_dict['price_target'] = None
        if download_short_interest and (ticker not in tickers_with_no_volume) and (ticker not in tickers_with_no_PT) and (ticker[0] != '^'):
            info_dict['short_interest'], info_dict['short_interest_prior'], info_dict['days_to_cover'], info_dict['trading_vol_avg'], info_dict['shares_float'] = web_scraper().short_interest(ticker=ticker)
        else:
            info_dict['short_interest'], info_dict['short_interest_prior'], info_dict['days_to_cover'], info_dict['trading_vol_avg'], info_dict['shares_float'] = None, None, None, None, None
    else:
        if (ticker not in tickers_with_no_volume) and (ticker not in ticker_group_dict['ETF database']) and (ticker not in tickers_with_no_PT) and (ticker[0] != '^'):
            info_dict['price_target'] = web_scrape().price_target(ticker=ticker)
        else:
            info_dict['price_target'] = None
        info_dict['short_interest'], info_dict['short_interest_prior'], info_dict['days_to_cover'], info_dict['trading_vol_avg'], info_dict['shares_float'] = None, None, None, None, None

    return info_dict


def get_ticker_data_dict(ticker: str = None, 
                         last_date = None,
                         verbose: bool = True, 
                         force_redownload: bool = False, 
                         smart_redownload: bool = False, 
                         download_today_data: bool = False, 
                         data_root_dir: str = None, 
                         auto_retry: bool = False,
                         keep_up_to_date: bool = False,
                         web_scraper = None,
                         download_short_interest: bool = False):

    """
    if keep_up_to_date is True, try to redownload if the last Date is not today
    """

    def process_and_save_raw_data():

        from ._ticker import Ticker, tickers_with_no_volume

        nonlocal ticker_history_df       
        ticker_history_df.to_csv(ticker_history_df_file, index=False)
        #
        history_df = pd.read_csv(ticker_history_df_file, index_col=False)
        if ticker in tickers_with_no_volume: # these have no volume
            history_df = history_df[(history_df['Close']>0) & (history_df['High']>0) & (history_df['Low']>0) & (history_df['Open']>0)]
            history_df['Volume'] = None
        else:
            history_df = history_df[(history_df['Close']>0) & (history_df['High']>0) & (history_df['Low']>0) & (history_df['Open']>0) & (history_df['Volume']>0)]
        history_df['Date'] = pd.to_datetime(history_df['Date'], format='%Y-%m-%d', utc=True) # "utc=True" is to be consistent with yfinance datetimes, which are received as UTC.
        #
        for year in [1,2,3,4,5,10,20,30]:
            ticker_info_dict[f'max_diff_pct_{year}yr']  = Ticker().max_diff_pct(ticker_history=history_df, days=365.25*year)
        #
        pickle.dump(ticker_info_dict, open(ticker_info_dict_file, "wb"))

    from ._ticker import global_data_root_dir, tickers_with_no_volume

    if ticker is None:
        raise ValueError("Error: ticker cannot be None")

    ticker = ticker.upper()

    if data_root_dir is None:
        data_root_dir = global_data_root_dir
    
    data_dir = data_root_dir / "ticker_data/yfinance"
    data_backup_dir = data_dir / "backup"

    if not data_dir.exists():
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            #os.makedirs(data_dir)
        except:
            raise IOError(f"cannot create data dir: {data_dir}")

    if not data_backup_dir.exists():
        try:
            data_backup_dir.mkdir(parents=True, exist_ok=True)
            #os.makedirs(data_backup_dir)
        except:
            raise IOError(f"cannot create data backup dir: {data_backup_dir}")

    ticker_history_df_file = data_dir / f"{ticker}_history.csv"
    ticker_info_dict_file = data_dir / f"{ticker}_info_dict.pkl"

    if (not ticker_history_df_file.is_file()) or (not ticker_info_dict_file.is_file()):

        try:
            ticker_history_df = download_ticker_history_df(ticker = ticker, verbose = verbose, download_today_data = download_today_data, auto_retry = auto_retry)
        except:
            raise SystemError("cannot download ticker history")

        try:
            ticker_info_dict = download_ticker_info_dict(ticker, verbose = verbose, auto_retry = auto_retry, web_scraper = web_scraper, download_short_interest = download_short_interest)
        except:
            raise SystemError("cannot download ticker info dict")

        process_and_save_raw_data()

    elif force_redownload or keep_up_to_date:

        curr_df = pd.read_csv(ticker_history_df_file, index_col=False)
        curr_info_dict = pd.read_pickle( ticker_info_dict_file )

        do_force_redownload = True

        if smart_redownload:
            if 'data_download_time' in curr_info_dict.keys():
                curr_last_date = curr_info_dict['data_download_time']
                if (datetime.now(tz=timezone.utc) - curr_last_date) <= timedelta(days=7):
                    do_force_redownload = False

        if keep_up_to_date:
            if 'data_download_time' in curr_info_dict.keys():
                curr_last_date = curr_info_dict['data_download_time']
                #if (datetime.now(tz=timezone.utc) - curr_last_date) <= timedelta(minutes=10):
                #if (datetime.now(tz=timezone.utc) - curr_last_date) <= timedelta(hours=1):
                if (datetime.now(tz=timezone.utc).date() - curr_last_date.date()) <= timedelta(days=0): # T1 = curr_last_date, T2 = now; if T2 is ahead of T1
                    do_force_redownload = False

        if do_force_redownload:
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
            if (curr_df.shape[0] - new_df.shape[0]) > 100:
                #raise ValueError(f"for ticker [{ticker}], the redownloaded df has fewer rows than the current one")
                print(f"ticker: [{ticker}]")
                print(f"*** The redownloaded df's rows [n={new_df.shape[0]}] are so much fewer (#<100) than that of the current one [n={curr_df.shape[0]}] --> the current one will be used instead")
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
                    ticker_info_dict = download_ticker_info_dict(ticker, verbose = verbose, auto_retry = auto_retry, web_scraper = web_scraper, download_short_interest = download_short_interest)
                except:
                    raise SystemError("cannot download ticker info dict")
                shutil.copy2( ticker_history_df_file, data_backup_dir )
                shutil.copy2( ticker_info_dict_file,  data_backup_dir )
                ticker_history_df = new_df
                process_and_save_raw_data()

    history_df = pd.read_csv(ticker_history_df_file, index_col=False)
    if ticker in tickers_with_no_volume: # these have no volume
        history_df = history_df[(history_df['Close']>0) & (history_df['High']>0) & (history_df['Low']>0) & (history_df['Open']>0)]
        history_df['Volume'] = None
    else:
        history_df = history_df[(history_df['Close']>0) & (history_df['High']>0) & (history_df['Low']>0) & (history_df['Open']>0) & (history_df['Volume']>0)]
    history_df['Typical'] = ( history_df['Close'] + history_df['High'] + history_df['Low'] ) / 3
    history_df['Date'] = pd.to_datetime(history_df['Date'], format='%Y-%m-%d', utc=True) # "utc=True" is to be consistent with yfinance datetimes, which are received as UTC.
    #
    if last_date is not None:
        history_df = history_df[history_df['Date']<=last_date]
    #
    try:
        info_dict = pd.read_pickle( ticker_info_dict_file )
    except:
        raise RuntimeError(f"ticker = {ticker}")
    if 'info' not in info_dict.keys():
        raise KeyError(f"for ticker = [{ticker}], 'info' is not in the info_dict keys")
    info_dict['history'] = history_df
    info_dict['ticker'] = ticker
    return info_dict


def get_formatted_ticker_data(ticker_data_dict, use_html: bool = False):
    from ._ticker import Ticker
    this_ticker = Ticker(ticker_data_dict=ticker_data_dict)

    if use_html:
        formatted_str = "<style>table, th, td {border: 1px solid black; border-collapse: collapse; padding: 2px;} body {font-family: Courier New;}</style><body>"
    else:
        formatted_str = ""

    if not 'info' in ticker_data_dict.keys():
        if use_html:
            formatted_str += f"the key 'info' does not exist in ticker_data_dict</body>"
        else:
            formatted_str += f"the key 'info' does not exist in ticker_data_dict"
        return formatted_str

    ticker_info = ticker_data_dict['info']
    if ticker_info is None:
        if use_html:
            formatted_str += f"the key 'info' does not exist in ticker_data_dict</body>"
        else:
            formatted_str += f"the key 'info' does not exist in ticker_data_dict"
        return formatted_str

    ticker_info_keys = ticker_info.keys()

    # name amd major indexes
    # major index
    df = pd.DataFrame({'DOW 30': this_ticker.in_dow30, 'NASDAQ 100': this_ticker.in_nasdaq100, 'S&P 500': this_ticker.in_sandp500, 'NASDAQ Composite': this_ticker.in_nasdaq_composite, 'Russell 1000': this_ticker.in_russell1000, 'Russell 2000': this_ticker.in_russell2000}, index=[0])
    if use_html:
        major_indexes_str = df.to_html(index=False).replace('<table border="1" class="dataframe">', '<table>').replace('True', '<b><span style=\"color:blue;\">True</span></b>').replace('False', '<span style=\"color:#D3D3D3;\">False</span>')
    else:
        major_indexes_str = df.to_string(index=False)
    #
    if use_html:
        ticker_name = f"<b>{this_ticker.name}</b><br/><br/>Symbol: [{this_ticker.symbol}]<br/>{major_indexes_str}"
    else:
        ticker_name = f"{this_ticker.name}\n\nSymbol: [{this_ticker.symbol}]\n\n{major_indexes_str}"

    # stock exchange listing info
    stock_exchange_info = ""
    if use_html:
        stock_exchange_info = f"<br/><hr>Exchange: {this_ticker.exchange}"
    else:
        stock_exchange_info = f"\n\nExchange: {this_ticker.exchange}"
    #
    if this_ticker.nasdaq_listed:
        if use_html:
            stock_exchange_info += f"<br/><hr>Nasdaq Listed<br/>- Name: [{this_ticker.nasdaq_security_name}]<br/>- Market category: [{this_ticker.nasdaq_market_category}]<br/>- Financial status: [{this_ticker.nasdaq_financial_status}]<br/>- ETF? [{this_ticker.nasdaq_etf}]"
        else:
            stock_exchange_info += f"\n\nNasdaq Listed\n- Name: [{this_ticker.nasdaq_security_name}]\n- Market category: [{this_ticker.nasdaq_market_category}]\n- Financial status: [{this_ticker.nasdaq_financial_status}]\n- ETF? [{this_ticker.nasdaq_etf}]"
    elif this_ticker.non_nasdaq_listed:
        if use_html:
            stock_exchange_info += f"<br/><hr>Exchange: {this_ticker.non_nasdaq_exchange}<br/>- Name: [{this_ticker.non_nasdaq_security_name}]<br/>- ETF? [{this_ticker.non_nasdaq_etf}]"
        else:
            stock_exchange_info += f"\n\nExchange: {this_ticker.non_nasdaq_exchange}\n- Name: [{this_ticker.non_nasdaq_security_name}]\n- ETF? [{this_ticker.non_nasdaq_etf}]"
    # ETF holdings
    if this_ticker.is_etf:
        if use_html:
            stock_exchange_info += f"<br/>- Portfolio Composition: <a href='https://screener.fidelity.com/ftgw/etf/snapshot/portfolioComposition.jhtml?symbols={this_ticker.symbol}'><b>{this_ticker.symbol}</b></a>"
        else:
            stock_exchange_info += f"\n- Portfolio Composition: https://screener.fidelity.com/ftgw/etf/snapshot/portfolioComposition.jhtml?symbols={this_ticker.symbol}"

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

    # short interest
    # indicator of bullish vs. bearish
    if use_html:
        short_info = f"<br/><hr>Short info unavailable"
    else:
        short_info = f"\n\nShort info unavailable"
    if this_ticker.short_interest_of_float is not None:
        if use_html:
            short_info = f"<br/><hr>Short percent of float: <b><span style='color:blue'>{this_ticker.short_interest_of_float*100:.2f}%</span></b>"
        else:
            short_info = f"\n\nShort percent of float: {this_ticker.short_interest_of_float*100:.2f}%"

    # valuation
    if (this_ticker.BVPS is not None) and (this_ticker.PB_ratio is not None):
        PB_ratio_str = f"{this_ticker.PB_ratio:.2f}"
    else:
        PB_ratio_str = "[N/A]"
    if use_html:
        valuation_info1 = f"<br/><hr>Valuation info (1)<br/><br/>The Price-to-Book ratio measures the market's valuation of a company relative to its book value. The current P/B ratio, dividing the current price by the most-recent-quarter (MRQ) BVPS, is <b>{PB_ratio_str}</b>.<br/><br/>The Price-to-Sales ratio reflects how much the market values every dollar of the company's sales. It takes a company's market share price and divide it by the company's total sales (or revenue) per share over the past 12 months. The lower the P/S ratio, the more attractive the investment.<br/><br/>This ratio can be effective in <b>valuing growth stocks that have yet to turn a profit</b> or have suffered a temporary setback.<br/><br/>As of today, check out <a href='https://www.gurufocus.com/term/ps/{this_ticker.symbol}/PS%252BRatio/'>gurufocus.com</a> and <a href='https://finance.yahoo.com/quote/{this_ticker.symbol}/key-statistics'>Yahoo Finance Valuation Measures</a> for details."
    else:
        valuation_info1 = f"\n\nValuation info (1)\n\nThe Price-to-Book ratio measures the market's valuation of a company relative to its book value. The current P/B ratio is {PB_ratio_str}."

    # earnings
    if use_html:
        earnings_info = f"<br/><hr><b><a href='https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/keyStatistics.jhtml?stockspage=keyStatistics&symbols={this_ticker.symbol}'>Valuation and Growth statistics</a></b><br/>"
    else:
        earnings_info = f"\n\nValuation and Growth statistics: https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/keyStatistics.jhtml?stockspage=keyStatistics&symbols={this_ticker.symbol}\n"
    
    if this_ticker.trailingEps is not None:
        if use_html:
            earnings_info += f"<br/>Diluted Earnings per share (EPS) from the last four quarters: <b><span style=\"color:blue;\">${this_ticker.trailingEps:+.2f}</span></b>;"
        else:
            earnings_info += f"\nDiluted Earnings per share (EPS) from the last four quarters: ${this_ticker.trailingEps:+.2f};"
    if this_ticker.forwardEps is not None:
        if use_html:
            earnings_info += f"<br/><br/>EPS estimated for the next four quarters: <b><span style=\"color:blue;\">${this_ticker.forwardEps:+.2f}</span></b>.<br/>" # , which is <b><span style=\"color:blue;\">{round(this_ticker.Eps_change_pct,2):+.2f}%</span></b>
        else:
            earnings_info += f"\n\nEPS estimated for the next four quarters: ${this_ticker.forwardEps:+.2f}.\n" # , which is {round(this_ticker.Eps_change_pct,2):+.2f}%
    if this_ticker.Eps_growth_rate is not None:
        if use_html:
            Eps_growth_rate_color = 'green' if this_ticker.Eps_growth_rate >= risk_free_interest_rate else 'red'
            earnings_info += f"<br/><a href='https://eresearch.fidelity.com/eresearch/evaluate/fundamentals/keyStatistics.jhtml?stockspage=keyStatistics&symbols={this_ticker.symbol}'>The 5-yr EPS growth rate</a> is estimated to be <b><span style=\"color:{Eps_growth_rate_color};\">{this_ticker.Eps_growth_rate:+.2f}%</span></b> (compound rate per year)<br/>"
        else:
            earnings_info += f"\nThe 5-yr EPS growth rate is estimated to be {this_ticker.Eps_growth_rate:+.2f}% (compound rate per year)\n"

    if use_html:
        earnings_info += f"<br/>Compared to risk-free interest rate: <b>{risk_free_interest_rate:+.2f}%</b>"
    else:
        earnings_info += f"\nCompared to risk-free interest rate: {risk_free_interest_rate:+.2f}%"

    # price target
    if use_html:
        price_target_info = f"<br/><hr>Price target info unavailable"
    else:
        price_target_info = f"\n\nPrice target info unavailable"

    if this_ticker.price_target is not None:
        up_side_pct = 100 * (this_ticker.price_target - this_ticker.last_close_price) / this_ticker.last_close_price
        PT_implied_continuous_compound_interest = 100 * np.log(this_ticker.price_target / this_ticker.last_close_price)
        PT_based_on_risk_free_rate = this_ticker.last_close_price * np.exp(risk_free_interest_rate/100)
        if use_html:
            price_target_info = f"<br/><hr>Price target:<br/><br/>- 1-yr price target: ${this_ticker.price_target:.1f} (compound interest: {PT_implied_continuous_compound_interest:.2f}%, <b><span style=\"color:blue;\">{up_side_pct:+.2f}%</span></b> upside)<br/>- 1-yr price target: ${PT_based_on_risk_free_rate:.1f} (based on risk-free interest rate: {risk_free_interest_rate:.2f}%)"
        else:
            price_target_info = f"\n\nPrice target:\n\n1-yr price target: ${this_ticker.price_target:.1f} (compound interest: {PT_implied_continuous_compound_interest:.2f}%, {up_side_pct:+.2f}% upside)\n- 1-yr price target: ${PT_based_on_risk_free_rate:.1f} (based on risk-free interest rate: {risk_free_interest_rate:.2f}%)"

    # apples-to-apples comparison
    # e.g., https://www.investopedia.com/terms/p/price-earningsratio.asp#investor-expectations
    if use_html:
        company_to_company_comparison_info = f"<br/><hr><b><a href='https://eresearch.fidelity.com/eresearch/evaluate/analystsOpinionsReport.jhtml?symbols={this_ticker.symbol}'>Research Reports</a></b>"
    else:
        company_to_company_comparison_info = f"\n\nResearch Reports: https://eresearch.fidelity.com/eresearch/evaluate/analystsOpinionsReport.jhtml?symbols={this_ticker.symbol}"

    if this_ticker.trailingPE is not None:
        if use_html:
            company_to_company_comparison_info += f"<br/><br/>For an apples-to-apples comparison, the ratio of current price to the earnings from the last four quarters (the trailing P/E, <b>the earnings multiple</b>): <b><span style=\"color:blue;\">{this_ticker.trailingPE:.2f}</span></b><br/><br/>A high P/E ratio could mean that an over-valued stock, or high expectation of growth rates in the future. Traditionally the P/E could be between 6 and 120, with a long-term mean of 15."
        else:
            company_to_company_comparison_info += f"\n\nFor an apples-to-apples comparison, the ratio of current price to the earnings from the last four quarters (the trailing P/E, the earnings multiple): {this_ticker.trailingPE:.2f} A high P/E ratio could mean that an over-valued stock, or high expectation of growth rates in the future. Traditionally the P/E could be between 6 and 120, with a long-term mean of 15."
        if this_ticker.forwardPE is not None:
            if use_html:
                company_to_company_comparison_info += f"<br/><br/>The ratio of current price to the earnings estimated for the next four quarters (the forward P/E, <b>the earnings multiple</b>): <b><span style=\"color:blue;\">{this_ticker.forwardPE:.2f}</span></b>. If the forward P/E ratio is lower (or higher) than the trailing P/E ratio, it means analysts are expecting earnings to increase (or decrease)."
            else:
                company_to_company_comparison_info += f"\n\nThe ratio of current price to the earnings estimated for the next four quarters (the forward P/E, the earnings multiple): {this_ticker.forwardPE:.2f}. If the forward P/E ratio is lower (or higher) than the trailing P/E ratio, it means analysts are expecting earnings to increase (or decrease)."
    if this_ticker.PEG_ratio is not None:
        if use_html:
            company_to_company_comparison_info += f"<br/><hr>The Price/Earnings-to-Growth (PEG) ratio is <b><span style=\"color:blue;\">{this_ticker.PEG_ratio}</span></b> (which is over-valued if &gt; 1.0, or under-valued if &lt; 1.0; in theory, the lower the PEG ratio the better, which implies paying less for future earnings growth.)"
        else:
            company_to_company_comparison_info += f"\n\nThe Price/Earnings-to-Growth (PEG) ratio is {this_ticker.PEG_ratio} (which is over-valued if > 1.0, or under-valued if < 1.0; in theory, the lower the PEG ratio the better, which implies paying less for future earnings growth.)"

    # shares info
    if use_html:
        shares_info = f"<br/><hr>Share info unavailable"
    else:
        shares_info = f"\n\nShare info unavailable"
    if 'floatShares' in ticker_info_keys and 'sharesOutstanding' in ticker_info_keys and 'marketCap' in ticker_info_keys:
        floatShares = this_ticker.floatShares
        sharesOutstanding = this_ticker.sharesOutstanding
        marketCap = ticker_info['marketCap']
        if floatShares is not None and sharesOutstanding is not None and marketCap is not None:
            if sharesOutstanding > 1e9:
                sharesOutstanding_info = f"{sharesOutstanding/1e9:.2f} billions"
            else:
                sharesOutstanding_info = f"{sharesOutstanding/1e6:.2f} millions"
            if marketCap > 1e12:
                marketCap_info = f"${marketCap/1e12:.2f} trillions"
            elif marketCap > 1e9:
                marketCap_info = f"${marketCap/1e9:.2f} billions"
            else:
                marketCap_info = f"${marketCap/1e6:.2f} millions"
            if sharesOutstanding != 0:
                if use_html:
                    shares_info = f"<br/><hr>Total number of shares issued: {sharesOutstanding_info} (<b><span style=\"color:blue;\">{floatShares/sharesOutstanding*100:.2f}%</span></b> freely tradable, which largely determines liquidity, while the other {100-floatShares/sharesOutstanding*100:.2f}% are held by institutions and insiders), and marketCap is {marketCap_info}."
                else:
                    shares_info = f"\n\nTotal number of shares issued: {sharesOutstanding_info} ({floatShares/sharesOutstanding*100:.2f}% freely tradable, which largely determines liquidity, while the other {100-floatShares/sharesOutstanding*100:.2f}% are held by institutions and insiders), and marketCap is {marketCap_info}."
            else:
                if use_html:
                    shares_info = f"<br/><hr>Total number of shares issued: {sharesOutstanding_info}, and marketCap is {marketCap_info}."
                else:
                    shares_info = f"\n\nTotal number of shares issued: {sharesOutstanding_info}, and marketCap is {marketCap_info}."
            
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
        valuation_info2 = f"<br/><hr>Valuation info (2) unavailable"
    else:
        valuation_info2 = f"/n/nValuation info (2) unavailable"
    # method1: cash flow (intrinsic valuation)
    # method2: multiple of performance (relative valuation)
    if this_ticker.EV_to_EBITDA is not None:
        if use_html:
            valuation_info2 = f"<br/><hr>Valuation info (2)<br/><br/>How much to buy a company? The firm's total value to its EBITDA (earnings before interest, taxes, depreciation, and amortization): <b><span style=\"color:blue;\">{this_ticker.EV_to_EBITDA:.2f}</span></b> (tends to be between 11-14, while below 10 is considered healthy; the lower, the better)"
        else:
            valuation_info2 = f"\n\nValuation info (2)\n\nHow much to buy a company? The firm's total value to its EBITDA (earnings before interest, taxes, depreciation, and amortization): {this_ticker.EV_to_EBITDA:.2f} (which tends to be between 11-14, while below 10 is considered healthy; the lower, the better)"

    # institutions
    if use_html:
        institutions_holding_info = f"<br/><hr>Institution holding info unavailable"
    else:
        institutions_holding_info = f"\n\nInstitution holding info unavailable"   
    if 'heldPercentInstitutions' in ticker_info_keys:
        percent_held_by_institutions = ticker_info['heldPercentInstitutions']
        if percent_held_by_institutions is not None:
            if use_html:
                institutions_holding_info = f"<br/><hr>Shares held by institutions: {100*percent_held_by_institutions:.2f}%<br/><br/>- Large % could be risky: when there is bad news, the price may plunge.<br/>- Low % could have more upside.<br/>- Increase in % is a good sign."
            else:
                institutions_holding_info = f"\n\nShares held by institutions: {100*percent_held_by_institutions:.2f}%\n\n- Large % could be risky: when there is bad news, the price may plunge.\n- Low % could have more upside.\n- Increase in % is a good sign."
            if 'institutional_holders' in ticker_data_dict.keys():
                institutional_holders_df = ticker_data_dict['institutional_holders']
                if institutional_holders_df is not None:
                    if all(elem in institutional_holders_df.columns for elem in ['% Out','Value']):
                        tmp_df = institutional_holders_df.drop(['% Out','Value'], axis=1, inplace=False) # axis: 0=row, 1=col
                        if 'sharesOutstanding' in ticker_info_keys:
                            sharesOutstanding = ticker_info['sharesOutstanding']
                            if sharesOutstanding is not None:
                                tmp_df['% Out'] = tmp_df['Shares'].apply(lambda x: f"{x/sharesOutstanding * 100:.2f}%")
                                tmp_df['Shares (mil.)'] = round(tmp_df['Shares'] / 1e6, 2)
                                if tmp_df['Shares'].max() * this_ticker.last_close_price / 1e9 < 1:
                                    tmp_df['Curr Value(mil.$)'] = round(tmp_df['Shares'] * this_ticker.last_close_price / 1e6, 2)
                                    tmp_df = tmp_df[['Holder','Shares (mil.)','Date Reported','% Out','Curr Value(mil.$)']]
                                else:
                                    tmp_df['Curr Value(bil.$)'] = round(tmp_df['Shares'] * this_ticker.last_close_price / 1e9, 2)
                                    tmp_df = tmp_df[['Holder','Shares (mil.)','Date Reported','% Out','Curr Value(bil.$)']]                                   
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
            if use_html:
                dividends_info += f"<br/><br/>Dividends yield in the past 12 mo: {this_ticker.last_1yr_dividends_pct:.2f}%"
            else:
                dividends_info += f"\n\nDividends yield in the past 12 mo: {this_ticker.last_1yr_dividends_pct:.2f}%"
            if 'payoutRatio' in ticker_info_keys:
                payoutRatio = ticker_info['payoutRatio']
                if payoutRatio is not None:
                    if use_html:
                        dividends_info += f"<br/><br/>As an evaluation of the dividend payment system, {payoutRatio*100:.2f}% of the earnings is paid out to shareholders."
                    else:
                        dividends_info += f"\n\nAs an evaluation of the dividend payment system, {payoutRatio*100:.2f}% of the earnings is paid out to shareholders."

    # measures
    if use_html:
        risk_info = f"<br/><hr>"
    else:
        risk_info = f"\n\n"
    years = [1,2,3,4,5,10,20,30]
    for year_n in years:
        max_diff_pct_yr_n = this_ticker.max_diff_pct_year_n(year_n=year_n)
        if (max_diff_pct_yr_n[0] is not None) and (max_diff_pct_yr_n[1] is not None):
            if use_html:
                risk_info += f" {year_n}yr_h/l(%): ({max_diff_pct_yr_n[0]:+,.0f}%, {max_diff_pct_yr_n[1]:+,.0f}%), ratio = {abs(max_diff_pct_yr_n[0]/max_diff_pct_yr_n[1] if max_diff_pct_yr_n[1] else 0):,.2f}<br/>"
            else:
                risk_info += f" {year_n}yr_h/l(%): ({max_diff_pct_yr_n[0]:+,.0f}%, {max_diff_pct_yr_n[1]:+,.0f}%), ratio = {abs(max_diff_pct_yr_n[0]/max_diff_pct_yr_n[1] if max_diff_pct_yr_n[1] else 0):,.2f}\n"
    # beta: covariance of stock with market
    if 'beta' in ticker_info_keys:
        beta = ticker_info['beta']
        if beta is not None:
            if use_html:
                risk_info += f"<br/>Beta: {beta:.2f}"
                if beta > 1.00:
                    risk_info += f" (more volatile than the overall market)<br/>"
                else:
                    risk_info += f" (less volatile than the overall market)<br/>"
            else:
                risk_info += f"\nBeta: {beta:.2f}"
                if beta > 1.00:
                    risk_info += f" (more volatile than the overall market)\n"
                else:
                    risk_info += f" (less volatile than the overall market)\n"
    # all-time high's and all-time low's
    all_time_highs_df = this_ticker.all_time_highs_df(n=10)
    all_time_lows_df = this_ticker.all_time_lows_df(n=10)
    fifty_two_weeks_high = this_ticker.fifty_two_weeks_high
    fifty_two_weeks_low = this_ticker.fifty_two_weeks_low
    if use_html:
        risk_info += f"<br/>52-wk high: ${fifty_two_weeks_high:.2f}<br/>52-wk low: ${fifty_two_weeks_low:.2f}<br/>"
        risk_info += f"<br/>All time highs: {all_time_highs_df.to_html(index=False, formatters={'High':'${:,.2f}'.format,'Date': lambda x: '{:%Y-%m-%d}'.format(pd.to_datetime(x, unit='D'))})}<br/>"
        risk_info += f"<br/>All time lows: {all_time_lows_df.to_html(index=False, formatters={'Low':'${:,.2f}'.format,'Date': lambda x: '{:%Y-%m-%d}'.format(pd.to_datetime(x, unit='D'))})}<br/>"
    else:
        risk_info += f"\n52-wk high: ${fifty_two_weeks_high:.2f}\n52-wk low: ${fifty_two_weeks_low:.2f}\n"
        risk_info += f"\nAll time highs: {all_time_highs_df.to_string(index=False, formatters={'High':'${:,.2f}'.format,'Date': lambda x: '{:%Y-%m-%d}'.format(pd.to_datetime(x, unit='D'))})}\n"
        risk_info += f"\nAll time lows: {all_time_lows_df.to_string(index=False, formatters={'Low':'${:,.2f}'.format,'Date': lambda x: '{:%Y-%m-%d}'.format(pd.to_datetime(x, unit='D'))})}\n"        

    # options
    if use_html:
        options_info = f"<hr>Options info unavailable"
    else:
        options_info = f"\nOptions info unavailable"
    if this_ticker.options is not None:
        if use_html:
            options_info = f"<hr>Options expirations: {this_ticker.options}"
        else:
            options_info = f"\nOptions expirations: {this_ticker.options}"
        if this_ticker.options != ():
            df = this_ticker.option_chain(expiration_date = this_ticker.options[0])
            if df is not None:
                df.drop(columns=['contractSymbol', 'lastTradeDate', 'contractSize', 'currency', 'bid', 'ask', 'change', 'volume'], inplace=True)
                calls = df[df['type'] == 'calls'].drop(columns=['type']).copy()
                #calls.drop(columns=['type'], inplace=True)
                puts = df[df['type'] == 'puts'].drop(columns=['type']).copy()
                #puts.drop(columns=['type'], inplace=True)
                for idx, row in calls.iterrows():
                    calls.loc[idx,'percentChange'] = f"{(calls.loc[idx,'percentChange']):.2f}%"
                    calls.loc[idx,'impliedVolatility'] = f"{(calls.loc[idx,'impliedVolatility']*100):+,.2f}%"
                for idx, row in puts.iterrows():
                    puts.loc[idx,'percentChange'] = f"{(puts.loc[idx,'percentChange']):.2f}%"
                    puts.loc[idx,'impliedVolatility'] = f"{(puts.loc[idx,'impliedVolatility']*100):+,.2f}%"
                if use_html:
                    options_info += f"<br/><br/>The most recent one (expiration: {this_ticker.options[0]}):<br/><br/>calls:{calls.to_html(index=False)}<br/><br/>puts:{puts.to_html(index=False)}"
                else:
                    options_info += f"\n\nThe most recent one (expiration: {this_ticker.options[0]}):\n\ncalls:{calls.to_string(index=False)}\n\nputs:{puts.to_string(index=False)}"

    # recommendations
    if use_html:
        recommendations_info = f"<br/><hr>Recommendations info unavailable"
    else:
        recommendations_info = f"\n\nRecommendations info unavailable"
    if this_ticker.recommendations is not None:
        recommend_n = 5
        if use_html:
            recommendations_info = f"<br/><hr>Recommendations (last {recommend_n}):<br\>" + this_ticker.recommendations.tail(recommend_n).to_html(index=False)
        else:
            recommendations_info = f"\n\nRecommendations (last {recommend_n}):\n" + this_ticker.recommendations.tail(recommend_n).to_string(index=False)

    # summary
    if 'longBusinessSummary' in ticker_info_keys:
        if use_html:
            long_business_summary = f"<br/><hr>{this_ticker.longBusinessSummary}"
        else:
            long_business_summary = f"\n\n{this_ticker.longBusinessSummary}"
    else:
        long_business_summary = ""

    # logo
    logo = ""
    if 'logo' in ticker_info_keys:
        if this_ticker.logo is not None:
            logo_base64 = base64.b64encode(this_ticker.logo)
            if logo_base64 is not None:
                if use_html:
                    logo = f"<br/><hr>Logo:<br/><img src=\"data:image/png;base64,{str(logo_base64,'utf-8')}\">"
                else:
                    if 'logo_url' in ticker_info_keys:
                        logo = f"\n\nLogo: {ticker_info['logo_url']}"

    if use_html:
        formatted_str += f"{ticker_name}{stock_exchange_info}{sector_info}{short_info}{valuation_info1}{valuation_info2}{earnings_info}{company_to_company_comparison_info}{shares_info}{institutions_holding_info}{profitability_info}{dividends_info}{risk_info}{options_info}{recommendations_info}{long_business_summary}{price_target_info}{logo}</body>"  
    else:
        formatted_str += f"{ticker_name}{stock_exchange_info}{sector_info}{short_info}{valuation_info1}{valuation_info2}{earnings_info}{company_to_company_comparison_info}{shares_info}{institutions_holding_info}{profitability_info}{dividends_info}{risk_info}{options_info}{recommendations_info}{long_business_summary}{price_target_info}{logo}"  
    
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


class web_scrape(object):
    def __init__(self):
        self.web_scrape_enable = False
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        if 'selenium' in installed:
            self.web_scrape_enable = True
            
    def price_target(self, ticker='AAPL', host='yahoo_finance'):
        from ._ticker import ticker_group_dict
        if ticker in ticker_group_dict['ETF'] or ticker in ticker_group_dict['ETF database']:
            return None
        if self.web_scrape_enable:
            from selenium import webdriver
            import re
            assert host in ['yahoo_finance',], "unexpected host"
            #print(f'web scraping [{ticker}] 1-yr price target on [{host}] ... ', end = '')
            options = webdriver.ChromeOptions()
            options.headless = True
            browser = webdriver.Chrome(options=options)
            if host == 'yahoo_finance':
                browser.get('https://finance.yahoo.com/quote/' + ticker.upper() )
            app = browser.find_element_by_id('app')
            self.price_target = None
            try:
                if host == 'yahoo_finance':
                    main = app.find_element_by_id('Main')
                    m = re.search('\n1y Target Est (.+?)\n', main.text)
                    if m is not None:
                        self.price_target = float(m.group(1))
                #print(f"{self.price_target:.2f}")
            except:
                #print("")
                pass
            browser.quit()
            return self.price_target


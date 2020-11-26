# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: GNU General Public License v3 (GPLv3)

import sys

import matplotlib
print(matplotlib.get_backend())
matplotlib.use('Qt5Agg') # backend

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QAction, qApp
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QComboBox, QCheckBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QCalendarWidget
from PyQt5.QtWidgets import QPushButton, QLabel, QProgressBar
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtCore import Qt, QThread, pyqtSignal

import copy

import pathlib
from os.path import join

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

from datetime import date, datetime, timedelta, timezone

from ..data import get_ticker_data_dict, get_formatted_ticker_data, Volume_Index, Moving_Average

import numpy as np
import pandas as pd

from matplotlib.widgets import Cursor

import warnings
import time

StyleSheet = '''
#ProgressBar {
    text-align: center;
    border-radius: 5px;
    border: 1px solid #009688;
}
#ProgressBar::chunk {
    background-color: #009688;
}
'''

ticker_group_dict = {'All': [],
                     'Basic Materials': ['DOW','HUN','EXP','AVTR','ECL','APD','DD','FNV','NEM','GDX','XLB'],
                     'Communication Services': ['CMCSA','DIS','EA','FB','GOOG','GOOGL','NFLX','ROKU','TMUS','VZ','ZM','T','TWTR','IRDM','TWLO','ESPO','XLC'],
                     'Consumer Cyclical': ['AMZN','BABA','HD','LOW','F','FIVE','JD','M','MCD','LGIH','MELI','PTON','NIO','NKE','OSTK','TSLA','TM','ARD','BERY','SBUX','BKNG','NCLH','W','XLY'],
                     'Consumer Defensive': ['BYND','KO','PG','COST','TGT','WMT','GIS','ACI','OLLI','SAM','PEP','XLP'],
                     'Energy': ['CVX','MUR','VLO','EQT','XOM','TOT','XLE'],
                     'Financial Services': ['AXP','BAC', 'BRK-B','C','GS','JPM','TRV','V','MA','WFC','MS','XLF','PYPL','BHF','MSCI','JEF'],
                     'Healthcare': ['ABT','ALGN','AMGN','BMY','INO','JNJ','MRK','MRNA','PFE','UNH','NVS','WBA','ABBV','BIIB','QDEL','LVGO','TLRY','ISRG','GILD','TMO','XLV'],
                     'Industrials': ['BA', 'CAT', 'DAL', 'FDX', 'HON', 'MMM','SPCE','LMT','UAL','EAF','ENR','GNRC','KODK','RTX','GE','WM','AAL','XLI'],
                     'Technology': ['AAPL','ADBE','AMD','AYX','CLDR','CRM','CRWD','CSCO','ENPH','FEYE','IBM','INTC','MSFT','NVDA','NVMI','NLOK','ONTO','QCOM','SPLK','TSM','UBER','FIT','SQ','CTXS','DOCU','LRCX','MCHP','MU','NXPI','SHOP','STMP','TXN','NOW','SNE','WDAY','XLK'],
                     'Utilities': ['PCG','D','DUK','XEL','NRG','ES','XLU'],
                     'Real Estate': ['AMT','CCI','PLD','BPYU','BDN','CSGP','XLRE'],
                     'Dividend Stocks (11/2020)': ['BMY','WMT','HD','AAPL','MSFT'],
                     'Growth Stocks (11/2020)': ['ALGN','FIVE','LGIH','MELI','PTON'],
                     'ETF': ['DIA', 'OILU', 'OILD', 'TQQQ', 'SQQQ', 'UDOW', 'SDOW', 'UVXY', 'SVXY', 'YANG', 'YINN', 'QQQ', 'VOO','SPY','IVV','TMF','TMV','TBF','TLT','ESPO','GDX','XLC','XLI','XLF','XLE','XLV','XLB','XLK','XLU','XLP','XLY','XLRE'],
                     'DOW30': ['GS','WMT','MCD','CRM','DIS','NKE','CAT','TRV','VZ','JPM','IBM','HD','INTC','AAPL','MMM','MSFT','JNJ','CSCO','V','DOW','MRK','PG','AXP','KO','AMGN','HON','UNH','WBA','CVX','BA'],
                     'S&P500': ['VOO','SPY','IVV','MMM','ABT','ABBV','ABMD','ACN','ATVI','ADBE','AMD','AAP','AES','AFL','A','APD','AKAM','ALK','ALB','ARE','ALXN','ALGN','ALLE','LNT','ALL','GOOGL','GOOG','MO','AMZN','AMCR','AEE','AAL','AEP','AXP','AIG','AMT','AWK','AMP','ABC','AME','AMGN','APH','ADI','ANSS','ANTM','AON','AOS','APA','AIV','AAPL','AMAT','APTV','ADM','ANET','AJG','AIZ','T','ATO','ADSK','ADP','AZO','AVB','AVY','BKR','BLL','BAC','BK','BAX','BDX','BRK-B','BBY','BIO','BIIB','BLK','BA','BKNG','BWA','BXP','BSX','BMY','AVGO','BR','BF-B','CHRW','COG','CDNS','CPB','COF','CAH','KMX','CCL','CARR','CTLT','CAT','CBOE','CBRE','CDW','CE','CNC','CNP','CERN','CF','SCHW','CHTR','CVX','CMG','CB','CHD','CI','CINF','CTAS','CSCO','C','CFG','CTXS','CLX','CME','CMS','KO','CTSH','CL','CMCSA','CMA','CAG','CXO','COP','ED','STZ','COO','CPRT','GLW','CTVA','COST','CCI','CSX','CMI','CVS','DHI','DHR','DRI','DVA','DE','DAL','XRAY','DVN','DXCM','FANG','DLR','DFS','DISCA','DISCK','DISH','DG','DLTR','D','DPZ','DOV','DOW','DTE','DUK','DRE','DD','DXC','EMN','ETN','EBAY','ECL','EIX','EW','EA','EMR','ETR','EOG','EFX','EQIX','EQR','ESS','EL','ETSY','EVRG','ES','RE','EXC','EXPE','EXPD','EXR','XOM','FFIV','FB','FAST','FRT','FDX','FIS','FITB','FE','FRC','FISV','FLT','FLIR','FLS','FMC','F','FTNT','FTV','FBHS','FOXA','FOX','BEN','FCX','GPS','GRMN','IT','GD','GE','GIS','GM','GPC','GILD','GL','GPN','GS','GWW','HAL','HBI','HIG','HAS','HCA','PEAK','HSIC','HSY','HES','HPE','HLT','HFC','HOLX','HD','HON','HRL','HST','HWM','HPQ','HUM','HBAN','HII','IEX','IDXX','INFO','ITW','ILMN','INCY','IR','INTC','ICE','IBM','IP','IPG','IFF','INTU','ISRG','IVZ','IPGP','IQV','IRM','JKHY','J','JBHT','SJM','JNJ','JCI','JPM','JNPR','KSU','K','KEY','KEYS','KMB','KIM','KMI','KLAC','KHC','KR','LB','LHX','LH','LRCX','LW','LVS','LEG','LDOS','LEN','LLY','LNC','LIN','LYV','LKQ','LMT','L','LOW','LUMN','LYB','MTB','MRO','MPC','MKTX','MAR','MMC','MLM','MAS','MA','MKC','MXIM','MCD','MCK','MDT','MRK','MET','MTD','MGM','MCHP','MU','MSFT','MAA','MHK','TAP','MDLZ','MNST','MCO','MS','MOS','MSI','MSCI','NDAQ','NOV','NTAP','NFLX','NWL','NEM','NWSA','NWS','NEE','NLSN','NKE','NI','NSC','NTRS','NOC','NLOK','NCLH','NRG','NUE','NVDA','NVR','ORLY','OXY','ODFL','OMC','OKE','ORCL','OTIS','PCAR','PKG','PH','PAYX','PAYC','PYPL','PNR','PBCT','PEP','PKI','PRGO','PFE','PM','PSX','PNW','PXD','PNC','POOL','PPG','PPL','PFG','PG','PGR','PLD','PRU','PEG','PSA','PHM','PVH','QRVO','PWR','QCOM','DGX','RL','RJF','RTX','O','REG','REGN','RF','RSG','RMD','RHI','ROK','ROL','ROP','ROST','RCL','SPGI','CRM','SBAC','SLB','STX','SEE','SRE','NOW','SHW','SPG','SWKS','SLG','SNA','SO','LUV','SWK','SBUX','STT','STE','SYK','SIVB','SYF','SNPS','SYY','TMUS','TROW','TTWO','TPR','TGT','TEL','FTI','TDY','TFX','TER','TSLA','TXT','TMO','TIF','TJX','TSCO','TT','TDG','TRV','TFC','TWTR','TYL','TSN','UDR','ULTA','USB','UAA','UA','UNP','UAL','UNH','UPS','URI','UHS','UNM','VLO','VAR','VTR','VTRS','VRSN','VRSK','VZ','VRTX','VFC','VIAC','V','VNT','VNO','VMC','WRB','WAB','WMT','WBA','DIS','WM','WAT','WEC','WFC','WELL','WST','WDC','WU','WRK','WY','WHR','WMB','WLTW','WYNN','XEL','XRX','XLNX','XYL','YUM','ZBRA','ZBH','ZION','ZTS'],
                     'Others': ['JWN','KSS','HMC','COST']}

ticker_group_dict['All'] = sorted(list(set([item for sublist in ticker_group_dict.values() for item in sublist])))

group_desc_dict = {'All': f"All unique tickers/symbols included in this app",
                   'Basic Materials': f"Companies engaged in the discovery, development, and processing of raw materials, which are used across a broad range of sectors and industries.",
                   'Communication Services': f"A broad range of companies that sell phone and internet services via traditional landline, broadband, or wireless.",
                   'Consumer Cyclical': f"A category of stocks that rely heavily on the business cycle and economic conditions.\n\nCompanies in the consumer discretionary sector sell goods and services that are considered non-essential, such as appliances, cars, and entertainment.",
                   'Consumer Defensive': f"A category of corporations whose sales and earnings remain relatively stable during both economic upturns and downturns.\n\nFor example, companies that manufacture food, beverages, household and personal products, packaging, or tobacco. Also includes companies that provide services such as education and training services. Defensive companies tend to make products or services that are essential to consumers.\n\nCompanies that produce and sell items considered essential for everyday use.",
                   'Energy': f"Companies focused on the exploration, production, and marketing of oil, gas, and renewable resources around the world.",
                   'Financial Services': f"Companies that offer services including loans, savings, insurance, payment services, and money management for individuals and firms.",
                   'Healthcare': f"A broad range of companies that sell medical products and services.",
                   'Industrials': f"Companies that produce machinery, equipment, and supplies that are used in construction and manufacturing, as well as providing related services.\n\nThese companies are closely tied to the economy, and their business volume often falls sharply during recessions, though each industrial subsector often performs differently.",
                   'Technology': f"Businesses that sell goods and services in electronics, software, computers, artificial intelligence, and other industries related to information technology (IT).",
                   'Utilities': f"Companies that provide electricity, natural gas, water, sewage, and other services to homes and businesses.",
                   'Real Estate': f"Companies that allow individual investors to buy shares in real estate portfolios that receive income from a variety of properties.",
                   'Dividend Stocks (11/2020)': f"Dividend Stocks (11/2020)",
                   'Growth Stocks (11/2020)': f"Growth Stocks (11/2020)",
                   'ETF': f"Exchange-traded fund",
                   'DOW30': f"Dow Jones Industrial Average 30 Components",
                   'S&P500': f"A stock market index that measures the stock performance of 500 large companies listed on stock exchanges in the United States.\n\nIndex funds that track the S&P 500 have been recommended as investments by Warren Buffett, Burton Malkiel, and John C. Bogle for investors with long time horizons.",
                   'Others': f"Others"}

App_name = "Investment Library"

# references: 
# https://matplotlib.org/api/widgets_api.html
# https://matplotlib.org/3.3.0/gallery/misc/cursor_demo.html
# https://matplotlib.org/users/event_handling.html
class SnappingCursor(Cursor):
    def __init__(self, plotline, name=None, UI=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x, self.y = plotline.get_data()
        self._last_index = None
        self.name = name
        self.UI = UI

    def onmove(self, event):
        if event.inaxes:
            if type(event.xdata) == np.float64:
                x_datetime = datetime(1970,1,1,tzinfo=timezone.utc) + timedelta(days=event.xdata)
                index = min(np.searchsorted(self.x, np.datetime64(x_datetime)), len(self.x)-1) # np.datetime64() is used to be congruent with self.x
                if index == self._last_index:
                    return  # still on the same data point. Nothing to do.
                self._last_index = index
                event.xdata = self.x[index]
                event.ydata = self.y[index]
                if self.name == 'ticker_canvas_cursor':
                    self.UI.ticker_canvas_coord_label.setText(f"date={pd.to_datetime(event.xdata).date()}, EMA9 price=${event.ydata:.2f}")
                if self.name == 'index_canvas_cursor':
                    self.UI.index_canvas_coord_label.setText(f"date={pd.to_datetime(event.xdata).date()}, EMA9 index={event.ydata:.2f}")
            super().onmove(event)


# reference: https://matplotlib.org/faq/usage_faq.html
class canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6.0, height=3.0, dpi=72, tight_layout=True, *args, **kwargs):
        self.figure = plt.figure(figsize=(width, height), dpi=dpi, tight_layout=tight_layout, *args, **kwargs)
        self.axes = self.figure.add_subplot(111)
        self.axes.tick_params(axis='both', which='major', labelsize=10.0)
        self.axes.tick_params(axis='both', which='minor', labelsize=8.0)
        super().__init__(self.figure)
        

class group_selection(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addItem("-- Select a sector or ticker group --")
        self.groups = list(ticker_group_dict.keys())
        for group in self.groups:
            self.addItem(group)    


class ticker_selection(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()
    
    def reset(self):
        self.clear()
        self.addItem("-- Select a ticker --")


class index_selection(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.clear()
        self.addItem("-- Select an index --")


class ticker_timeframe_selection(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.clear()
        self.addItem("-- Select a ticker canvas time frame --")


class ticker_lastdate_pushbutton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.setText("Select a last date on the timeline")
        self.setEnabled(False)


class ticker_download_latest_data_from_yfinance_pushbutton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.setText("Download latest data from the Internet")
        self.setEnabled(False)

            
class ticker_lastdate_calendar(QCalendarWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectedDate(date.today())


class ticker_lastdate_calendar_dialog(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle("Select a last date on the timeline")
        self.ticker_lastdate_calendar_use_last_available_date_button = QPushButton('Use the last available date in the data')
        self.ticker_lastdate_calendar = ticker_lastdate_calendar()
        self.ticker_lastdate_calendar_dialog_ok_button = QPushButton('Done')
        self.layout = QGridLayout()
        self.layout.addWidget(self.ticker_lastdate_calendar_use_last_available_date_button, 0, 0)
        self.layout.addWidget(self.ticker_lastdate_calendar, 1, 0)
        self.layout.addWidget(self.ticker_lastdate_calendar_dialog_ok_button, 2, 0)
        self.setLayout(self.layout)


class message_dialog(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle("Message Box")
        self.textinfo = textinfo()
        self.textinfo_ok_button = QPushButton('Ok')
        self.layout = QGridLayout()
        self.layout.addWidget(self.textinfo, 0, 0)
        self.layout.addWidget(self.textinfo_ok_button, 1, 0)
        self.setLayout(self.layout)


class index_canvas_options(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()

    def reset(self):
        self.clear()
        self.addItem("-- Select an index canvas option --")


class textinfo(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))


from ..__about__ import (
    __version__,
    __license__,
)

class about_dialog(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle(f"About {App_name}")
        self.aboutText = QLabel(parent=self)
        self.aboutText.setTextFormat(Qt.RichText)
        self.aboutText.setText(f"This App provides an UI to help with investment.<br/><br/>Version: {__version__}<br/>License: {__license__}<br/>PyPI: <a href=\"https://pypi.org/project/investment/\">https://pypi.org/project/investment/</a>")
        self.aboutText.setOpenExternalLinks(True)
        self.close_button = QPushButton('Close', parent=self)
        self.layout = QGridLayout()
        self.layout.addWidget(self.aboutText, 0, 0)
        self.layout.addWidget(self.close_button, 1, 0)
        self.setLayout(self.layout)
        self.close_button.clicked.connect(self._close_button_clicked)

    def _close_button_clicked(self):
        self.hide()


class preferences_dialog(QDialog):
    def __init__(self, parent=None, force_redownload_yfinance_data = None, download_today_data = None, data_root_dir = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.setWindowTitle("Preference Settings")
        self.checkbox_force_redownload_yfinance_data = QCheckBox("When viewing an individual ticker's history data, do not use any existing cache but download latest data from the Internet ?", parent=self)
        self.checkbox_download_today_data = QCheckBox("When downloading latest data from the Internet, include today's data (which may be incomplete if market still opens) ?", parent=self)
        self.label_data_root_dir = QLabel(parent=self)
        self.data_root_dir = data_root_dir
        self.label_data_root_dir.setText(f"Directory to store cache data: <span style=\"color:blue\">{data_root_dir}</span>")
        self.label_data_root_dir.setTextFormat(Qt.RichText)
        self.force_redownload_yfinance_data = force_redownload_yfinance_data
        self.download_today_data = download_today_data
        self.checkbox_force_redownload_yfinance_data.setChecked(self.force_redownload_yfinance_data)            
        self.checkbox_force_redownload_yfinance_data.stateChanged.connect(self._checkbox_force_redownload_yfinance_data_state_changed)
        self.checkbox_download_today_data.setChecked(self.download_today_data)
        self.checkbox_download_today_data.stateChanged.connect(self._checkbox_download_today_data_state_changed)
        self.close_button = QPushButton('Close', parent=self)
        self.layout = QGridLayout()
        self.layout.addWidget(self.checkbox_force_redownload_yfinance_data, 0, 0)
        self.layout.addWidget(self.checkbox_download_today_data, 1, 0)
        self.layout.addWidget(self.label_data_root_dir, 2, 0)
        self.layout.addWidget(self.close_button, 3, 0)
        self.setLayout(self.layout)
        self.close_button.clicked.connect(self._close_button_clicked)

    def _checkbox_force_redownload_yfinance_data_state_changed(self):
        self.force_redownload_yfinance_data = self.checkbox_force_redownload_yfinance_data.isChecked()

    def _checkbox_download_today_data_state_changed(self):
        self.download_today_data = self.checkbox_download_today_data.isChecked()

    def _close_button_clicked(self):
        self.hide()


# reference: https://pythonpyqt.com/pyqt-progressbar/
class ticker_thread(QThread):
    _signal = pyqtSignal(int, str)
    def __init__(self, app_window=None):
        super().__init__()
        self.app_window = app_window
    def run(self):
        for idx, ticker in enumerate(ticker_group_dict['All']):
            try:
                #time.sleep(0.001)
                get_ticker_data_dict(ticker = ticker, force_redownload = True, download_today_data = self.app_window.app_menu.preferences_dialog.download_today_data, data_root_dir = self.app_window.app_menu.preferences_dialog.data_root_dir)
            except:
                print(f"ticker = {ticker}")
                warnings.warn("*** Unable to download this ticker")
            self._signal.emit(idx+1, ticker)


class download_all_data_dialog(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.n_tickers = len(ticker_group_dict['All'])
        self.setWindowTitle("Download all data and store as cache")
        self.label = QLabel(parent=self)
        self.label.setText(f"Ready to download the latest data of all {len(ticker_group_dict['All'])} tickers included in this App and store as cache?\nNote: the data will be 400M+ and the process will take about ~50 minutes.")
        self.download_progressbar = QProgressBar(parent=self, objectName="ProgressBar")
        self.download_button = QPushButton(parent=self)
        self.close_button = QPushButton(parent=self)
        self.layout = QGridLayout()
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.download_progressbar, 1, 0)
        self.layout.addWidget(self.download_button, 2, 0)
        self.layout.addWidget(self.close_button, 3, 0)
        self.setLayout(self.layout)
        self.download_button.clicked.connect(self._download_button_clicked)
        self.close_button.clicked.connect(self._close_button_clicked)
        self.app_window = parent
        self._reset()

    def _reset(self):
        self.download_progressbar.setMinimum(0)
        self.download_progressbar.setMaximum(self.n_tickers)
        self.download_progressbar.setValue(0)
        self.download_button.setText('Yes, please download')
        self.close_button.setText('No, please skip this optional process')
        self.download_button.setEnabled(True)
        self.close_button.setEnabled(True)
        self.download_button.setDefault(True)

    def _close_button_clicked(self):
        self._reset()
        self.hide()

    def _download_button_clicked(self):
        self.download_button.setEnabled(False)
        self.close_button.setEnabled(False)
        # the reason to use this ticker_thread() is because in MacOS, there is an update problem in PyQt5
        # specifically, if there is any 'external' function call, like get_ticker_data_dict(), or even time.sleep(), after 'self.download_progressbar.setValue(idx)' in the _download_this_ticker() function
        # then the download_progressbar update won't show.
        # it is like we need to remove any external function call in self.download_progressbar.setValue(idx) in the signal.connect(), in MacOS
        # to see the effect, try to uncomment the # time.sleep(0.003) statement below; you will see how unsmooth it is.
        self.thread=ticker_thread(app_window=self.app_window)
        self.thread._signal.connect(self._download_this_ticker)
        self.thread.start()

    def _download_this_ticker(self, idx: int = None, ticker: str = None):
        self.download_progressbar.setValue(idx)
        #time.sleep(0.003)
        if idx == self.n_tickers:
            self.close_button.setText('Download completed. Return to App')
            self.close_button.setEnabled(True)
            self.close_button.setDefault(True)
            self.close_button.repaint()


class app_menu(object):
    def __init__(self, app_window=None):
        self.app_window = app_window
        self._default_preference_settings()
        self.about_dialog = about_dialog(parent=self.app_window)
        self.preferences_dialog = preferences_dialog(parent=self.app_window, force_redownload_yfinance_data=self.force_redownload_yfinance_data, download_today_data=self.download_today_data, data_root_dir=self.data_root_dir)
        self.download_all_data_dialog = download_all_data_dialog(parent=self.app_window)
        # about
        aboutAct = QAction('&About', parent=self.app_window)
        aboutAct.setShortcut('Ctrl+A')
        aboutAct.setStatusTip('About this app')
        aboutAct.triggered.connect(self.about_dialog.exec)
        # preferences
        prefAct = QAction('&Preferences...', parent=self.app_window)
        prefAct.setShortcut('Ctrl+,')
        prefAct.setStatusTip('Preference settings')
        prefAct.triggered.connect(self.preferences_dialog.exec)
        # download data
        download_all_Act = QAction('&Download all data', parent=self.app_window)
        download_all_Act.setShortcut('Ctrl+D')
        download_all_Act.setStatusTip('Download the latest data of all the 600+ tickers included in this App to cache')
        download_all_Act.triggered.connect(self.download_all_data_dialog.exec)        
        # exit
        exitAct = QAction('&Exit', parent=self.app_window)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit app')
        exitAct.triggered.connect(qApp.quit)
        # menubar
        self.app_window.menubar = self.app_window.menuBar()
        self.app_window.menubar.setNativeMenuBar(False)
        # appMenu
        self.app_window.AppMenu = self.app_window.menubar.addMenu('&App')
        self.app_window.AppMenu.addAction(aboutAct)
        self.app_window.AppMenu.addAction(prefAct)
        self.app_window.AppMenu.addAction(download_all_Act)
        self.app_window.AppMenu.addAction(exitAct)

    def _default_preference_settings(self):
        self.force_redownload_yfinance_data = False
        self.download_today_data = False
        self.data_root_dir = join(str(pathlib.Path.home()), ".investment")


class app_window(QMainWindow):
    def __init__(self, app=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # screen
        screen = app.primaryScreen()
        dpi = 72/screen.devicePixelRatio()
        width = screen.availableGeometry().width() * 0.95
        height = screen.availableGeometry().height() * 0.70

        # menuBar
        self.app_menu = app_menu(app_window=self)
        # central widget
        self.UI = UI(parent=self, app_window=self, dpi=dpi)
        self.setCentralWidget(self.UI)
        # others
        self.setWindowTitle(f"{App_name}")
        self.resize(width, height)
        #self.setGeometry(300, 300, 300, 200)


class UI(QWidget):
    def __init__(self, app_window=None, dpi=72, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_window = app_window

        self.group_selection = group_selection()
        self.ticker_selection = ticker_selection()
        self.ticker_textinfo = textinfo()
        self.ticker_textinfo.setFixedHeight(400)

        self.index_selection = index_selection()
        self.index_textinfo = textinfo()
        self.index_textinfo.setFixedHeight(400)

        self.ticker_timeframe_selection = ticker_timeframe_selection()
        self.ticker_lastdate_pushbutton = ticker_lastdate_pushbutton()
        self.ticker_download_latest_data_from_yfinance_pushbutton = ticker_download_latest_data_from_yfinance_pushbutton()
        self.ticker_canvas_coord_label = QLabel(parent=self, text='')
        self.ticker_lastdate_calendar_dialog = ticker_lastdate_calendar_dialog(parent=self)
        self.ticker_canvas = canvas(parent=self, dpi=dpi)
        self.index_canvas_options = index_canvas_options()
        self.index_canvas_coord_label = QLabel(parent=self, text='')
        self.index_canvas = canvas(parent=self, dpi=dpi)

        self.message_dialog = message_dialog(parent=self)

        # the layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.group_selection,  0, 0, 1, 1)
        self.layout.addWidget(self.ticker_selection, 0, 1, 1, 1)
        self.layout.addWidget(self.ticker_textinfo,  1, 0, 2, 2, Qt.AlignTop)
        self.layout.addWidget(self.index_selection,  3, 0, 1, 1)
        self.layout.addWidget(self.index_textinfo,   4, 0, 2, 2, Qt.AlignTop)
        self.layout.addWidget(self.ticker_timeframe_selection, 0, 2)
        self.layout.addWidget(self.ticker_lastdate_pushbutton, 0, 3)
        self.layout.addWidget(self.ticker_download_latest_data_from_yfinance_pushbutton, 0, 4)
        self.layout.addWidget(self.ticker_canvas_coord_label, 0, 5)
        self.layout.addWidget(self.ticker_canvas, 1, 2, 2, 4)
        self.layout.addWidget(self.index_canvas_options, 3, 2)
        self.layout.addWidget(self.index_canvas_coord_label, 3, 3)
        self.layout.addWidget(self.index_canvas,  4, 2, 2, 4)
        self.setLayout(self.layout)

        # control
        self.control = UI_control(UI = self)


class UI_control(object):

    def __init__(self, UI):
        super().__init__()
        self._UI = UI
        # connect signals
        self._UI.group_selection.currentIndexChanged.connect(self._group_selection_change)
        self._UI.ticker_selection.currentIndexChanged.connect(self._ticker_selection_change)
        self._UI.ticker_timeframe_selection.currentIndexChanged.connect(self._ticker_timeframe_selection_change)
        self._UI.ticker_lastdate_pushbutton.clicked.connect(self._ticker_lastdate_pushbutton_clicked)
        self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar_use_last_available_date_button.clicked.connect(self._ticker_lastdate_dialog_use_last_available_date_button_clicked)
        self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar_dialog_ok_button.clicked.connect(self._ticker_lastdate_dialog_ok_button_clicked)
        self._UI.ticker_download_latest_data_from_yfinance_pushbutton.clicked.connect(self._ticker_download_latest_data_from_yfinance)
        self._UI.message_dialog.textinfo_ok_button.clicked.connect(self._message_dialog_textinfo_ok_button_clicked)
        self._UI.index_canvas_options.currentIndexChanged.connect(self._index_canvas_options_change)
        self.timeframe_text = None
        self.ticker_data_dict_in_effect = None
        self._ticker_selected = False
        self.selected_ticker = None
        self.ticker_canvas_cursor = None
        self.index_canvas_cursor = None
        self.timeframe_dict = {"1 month": 1/12, "2 months": 1/6, "3 months": 1/4, "6 months": 1/2, "1 year": 1.0, "2 years": 2.0, "5 years": 5.0, "10 years": 10.0, "All time": float('inf')}
        self.time_last_date = pd.to_datetime(date.today())
        self.timeframe_selection_index = 5
        self.index_options_selection_index = 1

    def _group_selection_change(self, index: int = None):
        if index > 0:
            group_selected = self._UI.group_selection.itemText(index)
            # ticker selection
            self._UI.ticker_selection.reset()
            for ticker in sorted(ticker_group_dict[group_selected]):
                self._UI.ticker_selection.addItem(ticker)
            # ticker texinfo
            self._UI.ticker_textinfo.setText(group_desc_dict[group_selected])
            # ticker frame selection
            self._UI.ticker_timeframe_selection.reset()
            # ticker canvas
            self._UI.ticker_canvas.axes.clear()
            self._UI.ticker_canvas.draw()
            self._UI.ticker_canvas_coord_label.clear()
            # index canvas
            self._UI.index_canvas.axes.clear()
            self._UI.index_canvas.draw()
            self._UI.index_canvas_coord_label.clear()
            # index selection
            self._UI.index_selection.reset()
            # index textinfo
            self._UI.index_textinfo.clear()
            # index canvas selection
            self._UI.index_canvas_options.reset()
            # ticker lastdate and redownload pushbuttons
            self._UI.ticker_lastdate_pushbutton.reset()
            self._UI.ticker_download_latest_data_from_yfinance_pushbutton.reset()
            # others
            self._ticker_selected = False

    def _ticker_selection_change(self, index: int = None):
        if index > 0:
            self.selected_ticker = self._UI.ticker_selection.itemText(index)

            self.ticker_data_dict_original = get_ticker_data_dict(ticker = self.selected_ticker, force_redownload = self._UI.app_window.app_menu.preferences_dialog.force_redownload_yfinance_data, download_today_data = self._UI.app_window.app_menu.preferences_dialog.download_today_data, data_root_dir=self._UI.app_window.app_menu.preferences_dialog.data_root_dir)
            self.ticker_data_dict_in_effect = copy.deepcopy(self.ticker_data_dict_original)
            self._calc_index()

            self._UI.ticker_textinfo.setText(get_formatted_ticker_data(self.ticker_data_dict_in_effect))

            self._UI.ticker_timeframe_selection.reset()
            for timeframe in self.timeframe_dict.keys():
                self._UI.ticker_timeframe_selection.addItem(timeframe)

            self.time_last_date = self.ticker_data_dict_in_effect['history']['Date'].iloc[-1]
            self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar.setMaximumDate(self.time_last_date)
            self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar.setSelectedDate(self.time_last_date)
            self._UI.ticker_lastdate_pushbutton.setText(f"Last Date: {str(self.time_last_date.date())}")
            self._UI.ticker_timeframe_selection.setCurrentIndex(self.timeframe_selection_index)

            self._UI.ticker_canvas_coord_label.clear()
            self._UI.index_canvas_coord_label.clear()
            self._draw_ticker_canvas()
            self._draw_index_canvas()

            self._UI.index_selection.reset()
            self._UI.index_selection.addItem("PVI and NVI")
            self._UI.index_selection.setCurrentIndex(1)
            self._UI.index_textinfo.setText(f"PVI (Positive Volume Index) reflects high-volume days and thus the crowd's feelings: When PVI_EMA9 is above (or below) PVI_EMA255, the crowd is optimistic (or turning pessimistic).\n\nNVI (Negative Volume Index) reflects low-volume days and thus what the non-crowd (e.g., 'smart money') may be doing: When NVI_EMA9 is above (or below) NVI_EMA255, the non-crowd (e.g., 'smart money') may be buying (or selling).")

            # index canvas selection
            self._UI.index_canvas_options.reset()
            self._UI.index_canvas_options.addItem("PVI")
            self._UI.index_canvas_options.addItem("NVI")
            self.index_options_selection_index = 1
            self._UI.index_canvas_options.setCurrentIndex(self.index_options_selection_index)

            self._UI.ticker_lastdate_pushbutton.setEnabled(True)
            self._UI.ticker_download_latest_data_from_yfinance_pushbutton.setEnabled(True)

            self._ticker_selected = True

    def _draw_ticker_canvas(self):
        canvas = self._UI.ticker_canvas
        canvas.axes.clear()
        ticker_plotline, = canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'], self.ticker_data_dict_in_effect['history']['Close_EMA9'],   'tab:blue',                     linewidth=1)
        canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'],                    self.ticker_data_dict_in_effect['history']['Close_EMA255'], 'tab:blue', linestyle="dashed", linewidth=1)
        canvas.axes.set_xlabel('Date', fontsize=10.0)
        canvas.axes.set_ylabel('Close Price (EMA9, 255)', fontsize=10.0)
        #################################################
        self.ticker_canvas_cursor = SnappingCursor(plotline=ticker_plotline, ax=canvas.axes, useblit=True, color='black', linestyle='dashed', linewidth=1, name='ticker_canvas_cursor', UI=self._UI)
        canvas.mpl_connect('motion_notify_event', self.ticker_canvas_cursor.onmove)
        #################################################
        canvas.draw()

    def _draw_index_canvas(self):
        canvas = self._UI.index_canvas
        canvas.axes.clear()
        index_plotline_PVI_EMA9, = canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'], self.ticker_data_dict_in_effect['history']['PVI_EMA9'],   color='tab:green',                      linewidth=1)
        canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'],                            self.ticker_data_dict_in_effect['history']['PVI_EMA255'], color='tab:green',  linestyle="dashed", linewidth=1)
        index_plotline_NVI_EMA9, = canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'], self.ticker_data_dict_in_effect['history']['NVI_EMA9'],   color='tab:orange',                     linewidth=1)
        canvas.axes.plot(self.ticker_data_dict_in_effect['history']['Date'],                            self.ticker_data_dict_in_effect['history']['NVI_EMA255'], color='tab:orange', linestyle="dashed", linewidth=1)
        canvas.axes.set_xlabel('Date', fontsize=10.0)
        canvas.axes.set_ylabel('PVI (green) and NVI (orange) (EMA9, 255)', fontsize=10.0)
        #################################################
        if self.index_options_selection_index == 1:
            index_plotline = index_plotline_PVI_EMA9
        elif self.index_options_selection_index == 2:
            index_plotline = index_plotline_NVI_EMA9
        else:
            raise ValueError("index options selection index not within range")
        self.index_canvas_cursor = SnappingCursor(plotline=index_plotline, ax=canvas.axes, useblit=True, color='black', linestyle='dashed', linewidth=1, name='index_canvas_cursor', UI=self._UI)
        canvas.mpl_connect('motion_notify_event', self.index_canvas_cursor.onmove)
        #################################################
        canvas.draw()

    def _index_canvas_options_change(self, index: int = None):
        if index > 0:
            self.index_options_text = self._UI.index_canvas_options.itemText(index)
            self.index_options_selection_index = index

            self._draw_index_canvas() 

    def _ticker_timeframe_selection_change(self, index: int = None):
        if index > 0:
            self.timeframe_text = self._UI.ticker_timeframe_selection.itemText(index)
            self.timeframe_selection_index = index

            if self.timeframe_text in self.timeframe_dict.keys():
                history_df = self.ticker_data_dict_original['history'].copy()
                if self.timeframe_text == "All time":
                    time_first_date = history_df['Date'].iloc[0]
                else:
                    time_first_date = self.time_last_date - timedelta(days=365.25*self.timeframe_dict[self.timeframe_text])
                history_df = history_df[(time_first_date<=history_df['Date']) & (history_df['Date']<=self.time_last_date)]
                if len(history_df) == 0:
                    self._UI.message_dialog.textinfo.setText(f"No data available in the specified date range: {str(time_first_date.date())} ~ {str(self.time_last_date.date())}")
                    self._UI.message_dialog.exec()
                    return
                self.ticker_data_dict_in_effect['history'] = history_df

            self._calc_index()
            self._draw_ticker_canvas()
            self._draw_index_canvas()

    def _calc_index(self):
        history_df = self.ticker_data_dict_in_effect['history']
        # positive volume index and negative volume index
        history_df['PVI_EMA9'], history_df['NVI_EMA9'], history_df['PVI_EMA255'], history_df['NVI_EMA255'] = Volume_Index(short_periods=9, long_periods=255).PVI_NVI(history_df['Close'], history_df['Volume'])
        history_df['Close_EMA9'], history_df['Close_EMA255'] = Moving_Average(periods=9).Exponential(history_df['Close']), Moving_Average(periods=255).Exponential(history_df['Close'])
        self.ticker_data_dict_in_effect['history'] = history_df

    def _ticker_lastdate_pushbutton_clicked(self):
        if self._ticker_selected:
            self._UI.ticker_lastdate_calendar_dialog.exec() # using .exec() instead of .show() to ensure that the dialog stays on the top

    def _ticker_download_latest_data_from_yfinance(self):
        if self._ticker_selected:
            self.ticker_data_dict_original = get_ticker_data_dict(ticker = self.selected_ticker, force_redownload = True, download_today_data=self._UI.app_window.app_menu.preferences_dialog.download_today_data, data_root_dir=self._UI.app_window.app_menu.preferences_dialog.data_root_dir)
            self._ticker_lastdate_dialog_use_last_available_date_button_clicked()
            self._UI.repaint()

    def _ticker_lastdate_dialog_use_last_available_date_button_clicked(self):
        self.time_last_date = self.ticker_data_dict_original['history']['Date'].iloc[-1]
        self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar.setMaximumDate(self.time_last_date)
        self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar.setSelectedDate(self.time_last_date)
        self._ticker_lastdate_dialog_any_button_clicked()

    def _ticker_lastdate_dialog_ok_button_clicked(self):
        self.time_last_date = pd.to_datetime(self._UI.ticker_lastdate_calendar_dialog.ticker_lastdate_calendar.selectedDate().toPyDate())
        self._ticker_lastdate_dialog_any_button_clicked()

    def _ticker_lastdate_dialog_any_button_clicked(self):
        if self._UI.ticker_lastdate_calendar_dialog.isVisible():
            self._UI.ticker_lastdate_calendar_dialog.hide()
        self._UI.ticker_lastdate_pushbutton.setText(f"Last Date: {str(self.time_last_date.date())}")
        self._ticker_timeframe_selection_change(self.timeframe_selection_index)

    def _message_dialog_textinfo_ok_button_clicked(self):
        self._UI.message_dialog.hide()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)
    window = app_window(app=app)
    window.show()
    sys.exit(app.exec())


def test():
    for ticker in ticker_group_dict['All']:
        print("\n<-------------------------------------------------------------------------------------------")
        print(get_formatted_ticker_data(get_ticker_data_dict(ticker=ticker, force_redownload=False, download_today_data=True)))
        print("------------------------------------------------------------------------------------------->\n")

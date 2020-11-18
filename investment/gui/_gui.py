# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: GNU General Public License v3 (GPLv3)

import sys

import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QFontDatabase

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

from ..data import get_ticker_data_dict

sector_tickers_dict = {'All': [],
                       'Communication Services': ['FB','GOOGL','NFLX','ZM'],
                       'Consumer Cyclical': ['AMZN','OSTK','TSLA'],
                       'Consumer Defensive': ['BYND','WMT',],
                       'Financial Services': ['BAC', 'BRK-B','C','JPM', 'WFC'],
                       'Healthcare': ['INO','MRNA','PFE'],
                       'Industrials': ['BA', 'DAL', 'FDX', 'SPCE',],
                       'ETF': ['OILU', 'OILD', 'TQQQ', 'SQQQ', 'UDOW', 'SDOW', 'UVXY', 'SVXY', 'YANG', 'YINN'],
                       'Technology': ['AAPL','AMD','AYX','CLDR', 'INTC', 'MSFT','NVDA','NVMI','ONTO','QCOM','SPLK','TSM','UBER'],
                       'Utilities': ['PCG',],
                       'Others': []}

sector_tickers_dict['All'] = sorted([item for sublist in sector_tickers_dict.values() for item in sublist])


class ticker_canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=4, height=4, dpi=72):
        self.figure = plt.figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        self.axes.tick_params(axis='both', which='major', labelsize=10)
        self.axes.tick_params(axis='both', which='major', labelsize=8)
        super().__init__(self.figure)


class sector_selection(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItem("-- Select a sector --")
        self.sectors = list(sector_tickers_dict.keys())
        for sector in self.sectors:
            self.addItem(sector)    


class ticker_selection(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItem("-- Select a ticker --")


class ticker_textinfo(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setCurrentFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))


class ticker_info_UI(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QVBoxLayout()
        self.sector_selection = sector_selection()
        self.ticker_selection = ticker_selection()
        self.ticker_textinfo = ticker_textinfo()
        self.ticker_canvas = ticker_canvas(parent=self)
        self.layout.addWidget(self.sector_selection)
        self.layout.addWidget(self.ticker_selection)
        self.layout.addWidget(self.ticker_textinfo)
        self.layout.addWidget(self.ticker_canvas)
        self.setLayout(self.layout)
        self.setWindowTitle('Ticker Info')
        self.resize(800, 800)


class ticker_info_control(object):
    def __init__(self, UI):
        super().__init__()
        self._UI = UI
        # connect signals
        self._UI.sector_selection.currentIndexChanged.connect(self._sector_selection_change)
        self._UI.ticker_selection.currentIndexChanged.connect(self._ticker_selection_change)

    def _sector_selection_change(self, index: int = None):
        if index > 0:
            sector_selected = self._UI.sector_selection.itemText(index)
            self._UI.ticker_selection.clear()
            self._UI.ticker_selection.addItem("-- Select a ticker --")
            for ticker in sorted(sector_tickers_dict[sector_selected]):
                self._UI.ticker_selection.addItem(ticker)


    def _ticker_selection_change(self, index: int = None):
        if index > 0:
            ticker_selected = self._UI.ticker_selection.itemText(index)

            ticker_data_dict = get_ticker_data_dict(ticker_selected)
            ticker_info = ticker_data_dict['info']
            info = ""
            for key in ticker_info.keys():
                info = f"{info}{key} = {ticker_info[key]}\n"
            self._UI.ticker_textinfo.setText(f"Info:\n{info}\n{ticker_data_dict['info']['shortName']}\n\nInstitutional Holders:\n{ticker_data_dict['institutional_holders']}\n\nDividends:\n{ticker_data_dict['dividends']}")

            canvas = self._UI.ticker_canvas
            canvas.axes.cla()
            canvas.axes.plot(ticker_data_dict['history'][['Close']], 'tab:blue')
            canvas.axes.set_ylabel('Close Price', fontsize=8)
            canvas.figure.tight_layout()
            canvas.draw()
        

def demo():
    app = QApplication(sys.argv)
    UI = ticker_info_UI()
    UI.show()
    UI_control = ticker_info_control(UI = UI)
    sys.exit(app.exec_())


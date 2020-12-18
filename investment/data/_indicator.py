# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import pandas as pd
import numpy as np

class momentum_indicator(object):
    def __init__(self, periods=14):
        super().__init__()
        self.periods = periods

    def RSI(self, close_price: np.ndarray):
        """
        https://www.investopedia.com/terms/r/rsi.asp
        """
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        up_periods = np.zeros(shape=n_periods, dtype=float)
        down_periods = np.zeros(shape=n_periods, dtype=float)
        RSI = np.zeros(shape=n_periods, dtype=float)
        up_periods[0] = 0
        down_periods[0] = 0
        for i in range(1, n_periods):
            if close_price[i]>close_price[i-1]:
                up_periods[i] = close_price[i] - close_price[i-1]
                down_periods[i] = 0
            elif close_price[i]<close_price[i-1]:
                up_periods[i] = 0
                down_periods[i] = close_price[i-1] - close_price[i]
            else:
                up_periods[i] = 0
                down_periods[i] = 0
        up   = moving_average(periods=self.periods).smoothed(up_periods)
        down = moving_average(periods=self.periods).smoothed(down_periods)
        for i in range(n_periods):
            if down[i] == 0:
                RSI[i] = 100
            elif up[i] == 0:
                RSI[i] = 0
            else:
                RSI[i] = 100 - 100/(1+up[i]/down[i])
        return RSI


# https://www.investopedia.com/terms/v/volume-analysis.asp
class volume_indicator(object):
    def __init__(self, short_periods=9, long_periods=255):
        super().__init__()
        self.short_periods = short_periods
        self.long_periods = long_periods
        
    def PVI_NVI(self, close_price: np.ndarray, volume: np.ndarray):
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        if all(volume==0):
            return [None]*n_periods, [None]*n_periods, [None]*n_periods, [None]*n_periods
        PVI = np.empty(shape=n_periods, dtype=float)
        NVI = np.empty(shape=n_periods, dtype=float)
        PVI[0] = 1000
        NVI[0] = 1000
        EMA_short_period_volume = moving_average(periods=self.short_periods).exponential(volume)
        use_EMA_short_period_volume = False # the reason to use EMA_short_periods not daily volume is to get a more even-keeled reference volume
        if use_EMA_short_period_volume:
            reference_volume = EMA_short_period_volume
        else:
            reference_volume = volume.copy()
        for today_idx in range(1, n_periods):
            if volume[today_idx] > reference_volume[today_idx-1]:
                PVI[today_idx] = PVI[today_idx-1] + ((close_price[today_idx] - close_price[today_idx-1]) / close_price[today_idx-1] * PVI[today_idx-1])
                NVI[today_idx] = NVI[today_idx-1]
            else:
                PVI[today_idx] = PVI[today_idx-1]
                NVI[today_idx] = NVI[today_idx-1] + ((close_price[today_idx] - close_price[today_idx-1]) / close_price[today_idx-1] * NVI[today_idx-1])
        PVI *= 100/np.max(PVI)
        NVI *= 100/np.max(NVI)
        return PVI, NVI, moving_average(periods=self.short_periods).exponential(PVI), moving_average(periods=self.short_periods).exponential(NVI), moving_average(periods=self.long_periods).exponential(PVI), moving_average(periods=self.long_periods).exponential(NVI)


class moving_average(object):
    def __init__(self, periods = 30, smoothing = 2):
        super().__init__()
        self.periods = periods
        self.smoothing = smoothing
        self.multiplier = self.smoothing / (1+self.periods)

    def smoothed(self, data_series: np.ndarray):
        """
        https://en.wikipedia.org/wiki/Moving_average
        """
        if type(data_series) == pd.Series:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        if n_periods<self.periods:
            return [None] * n_periods
        elif n_periods == self.periods:
            return [None] * (self.periods-1) + [data_series.mean()]
        else:
            SMMA = np.empty(shape=n_periods, dtype=float)
            for i in range(self.periods-1):
                SMMA[i] = None
            SMMA[self.periods-1] = data_series[:self.periods].mean()
            for idx in range(self.periods, n_periods):
                SMMA[idx] = ((self.periods-1)*SMMA[idx-1] + data_series[idx])/self.periods
            return SMMA

    def exponential(self, data_series: np.ndarray):
        if type(data_series) == pd.Series:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        EMA = np.empty(shape=n_periods, dtype=float)
        EMA[0] = data_series[0]
        for idx in range(1, n_periods):
            EMA[idx] = (data_series[idx] * self.multiplier) + (EMA[idx-1] * (1-self.multiplier))
        return EMA

    def simple(self, data_series: np.ndarray):
        if type(data_series) == pd.Series:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        SMA = np.empty(shape=n_periods, dtype=float)
        data = np.array(data_series)
        for idx in range(n_periods):
            if idx >= (self.periods-1):
                SMA[idx] = np.mean(data[(idx-self.periods+1):(idx+1)])
            else:
                SMA[idx] = np.nan
        return SMA
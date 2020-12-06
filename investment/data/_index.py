# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import pandas as pd
import numpy as np

# https://www.investopedia.com/terms/v/volume-analysis.asp
class Volume_Index(object):
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
        PVI = np.empty(shape=n_periods, dtype=float)
        NVI = np.empty(shape=n_periods, dtype=float)
        PVI[0] = 1.0
        NVI[0] = 1.0
        EMA_short_period_volume = Moving_Average(periods=self.short_periods).Exponential(volume)
        use_EMA_short_period_volume = True # the reason to use EMA_short_periods not daily volume is to get a more even-keeled reference volume
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
        return Moving_Average(periods=self.short_periods).Exponential(PVI), Moving_Average(periods=self.short_periods).Exponential(NVI), Moving_Average(periods=self.long_periods).Exponential(PVI), Moving_Average(periods=self.long_periods).Exponential(NVI)


class Moving_Average(object):
    def __init__(self, periods = 30, smoothing = 2):
        super().__init__()
        self.periods = periods
        self.smoothing = smoothing
        self.multiplier = self.smoothing / (1+self.periods)

    def Exponential(self, data_series: np.ndarray):
        if type(data_series) == pd.Series:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        EMA = np.empty(shape=n_periods, dtype=float)
        EMA[0] = data_series[0]
        for idx in range(1, n_periods):
            EMA[idx] = (data_series[idx] * self.multiplier) + (EMA[idx-1] * (1-self.multiplier))
        return EMA

    def Simple(self, data_series: np.ndarray):
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
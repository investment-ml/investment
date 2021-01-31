# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import pandas as pd
import numpy as np

class volatility_indicator(object):
    def __init__(self):
        super().__init__()

    def Bollinger_Band(self, typical_price: np.ndarray, n_smoothing_days = 20, n_std_dev = 2):
        """
        https://www.investopedia.com/terms/b/bollingerbands.asp
        """
        if type(typical_price) == pd.Series:
            typical_price = typical_price.to_numpy()
        n_periods = typical_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        MA = moving_average(periods = n_smoothing_days).simple(typical_price)
        sigma = np.zeros(shape=n_periods, dtype=float)
        for idx in range(n_periods):
            if idx < n_smoothing_days:
                sigma[idx] = np.nan
            else:
                sigma[idx] = np.std(typical_price[(idx-n_smoothing_days):(idx)])
        BOLU = MA + n_std_dev * sigma
        BOLD = MA - n_std_dev * sigma
        return MA, BOLU, BOLD

class momentum_indicator(object):
    def __init__(self):
        super().__init__()

    def RSI(self, close_price: np.ndarray, RSI_periods: int = 14):
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
        up   = moving_average(periods=RSI_periods).smoothed(up_periods)
        down = moving_average(periods=RSI_periods).smoothed(down_periods)
        for i in range(n_periods):
            if down[i] == 0:
                RSI[i] = 100
            elif up[i] == 0:
                RSI[i] = 0
            else:
                RSI[i] = 100 - 100/(1+up[i]/down[i])
        return RSI

    def money_flow(self, high_price: np.ndarray, low_price: np.ndarray, close_price: np.ndarray, volume: np.ndarray, periods = 14):
        """
        https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/MFI
        """
        if type(high_price) == pd.Series:
            high_price = high_price.to_numpy()       
        if type(low_price) == pd.Series:
            low_price = low_price.to_numpy()       
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()        
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        if any(volume==None):
            return [None]*n_periods
        typical_price = (high_price + low_price + close_price)/3
        money_flow = typical_price * volume
        positive_money_flow = np.zeros(shape=n_periods, dtype=float)
        negative_money_flow = np.zeros(shape=n_periods, dtype=float)
        MFI = np.zeros(shape=n_periods, dtype=float) # https://en.wikipedia.org/wiki/Money_flow_index
        for today_idx in range(periods):
            MFI[today_idx] = None
        for today_idx in range(periods, n_periods):
            for idx in range(periods):
                if typical_price[today_idx-idx] > typical_price[today_idx-idx-1]:
                    positive_money_flow[today_idx] += money_flow[today_idx-idx]
                elif typical_price[today_idx-idx] < typical_price[today_idx-idx-1]:
                    negative_money_flow[today_idx] += money_flow[today_idx-idx]
            MFI[today_idx] = 100 * positive_money_flow[today_idx] / (positive_money_flow[today_idx]+negative_money_flow[today_idx])
        return MFI
        
    def MACD(self, close_price: np.ndarray, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        https://www.investopedia.com/terms/m/macd.asp
        """
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        fast_EMA = moving_average(periods=fast_period).exponential(close_price)
        slow_EMA = moving_average(periods=slow_period).exponential(close_price)
        macd = fast_EMA - slow_EMA # when fast > slow, it's positive
        signal = moving_average(periods=signal_period).exponential(macd)
        histogram = macd - signal
        return macd, signal, histogram
    
    def OBV(self, close_price: np.ndarray, volume: np.ndarray):
        """
        https://www.investopedia.com/terms/o/onbalancevolume.asp
        """
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = close_price.shape[0]
        if any(volume==None):
            return [None]*n_periods
        obv = np.zeros(shape=n_periods, dtype=float)
        obv[0] = 0
        for idx in range(1, n_periods):
            if close_price[idx] > close_price[idx-1]:
                obv[idx] = obv[idx-1] + volume[idx] # *close_price[idx]*(close_price[idx]-close_price[idx-1])
            elif close_price[idx] < close_price[idx-1]:
                obv[idx] = obv[idx-1] - volume[idx] # *close_price[idx]*(close_price[idx-1]-close_price[idx])
            else:
                obv[idx] = obv[idx-1]
        return obv

    def Z_price_vol(self, close_price: np.ndarray, volume: np.ndarray):
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = volume.shape[0]
        if any(volume==None):
            return [None]*n_periods
        price_vol = close_price * volume
        Z_price_vol = (price_vol - price_vol.mean())/(price_vol.std())
        return Z_price_vol

# https://www.investopedia.com/terms/v/volume-analysis.asp
class volume_indicator(object):
    def __init__(self, short_periods=9, long_periods=255):
        super().__init__()
        self.short_periods = short_periods
        self.long_periods = long_periods

    def accumulation_distribution(self, high_price: np.ndarray, low_price: np.ndarray, close_price: np.ndarray, volume: np.ndarray):
        """
        https://www.investopedia.com/terms/a/accumulationdistribution.asp
        """
        if type(high_price) == pd.Series:
            high_price = high_price.to_numpy()       
        if type(low_price) == pd.Series:
            low_price = low_price.to_numpy()       
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()        
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        if any(volume==None):
            return [None]*n_periods, [None]*n_periods
        ad = np.zeros(shape=n_periods, dtype=float)
        if high_price[0] == low_price[0]:
            ad[0] = 0
        else:
            ad[0] = ((close_price[0] - low_price[0]) - (high_price[0] - close_price[0])) / (high_price[0] - low_price[0]) * volume[0] # CMFV: Current money flow volume
        for today_idx in range(1, n_periods):
            if low_price[today_idx] == high_price[today_idx]:
                CMFV = 0
            else:
                CMFV = ((close_price[today_idx] - low_price[today_idx]) - (high_price[today_idx] - close_price[today_idx])) / (high_price[today_idx] - low_price[today_idx]) * volume[today_idx]
            ad[today_idx] = ad[today_idx-1] + CMFV
        Z_ad = (ad - ad.mean())/(ad.std())
        return ad, Z_ad
        
    def PVI_NVI(self, close_price: np.ndarray, volume: np.ndarray):
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        if type(volume) == pd.Series:
            volume = volume.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        if any(volume==None):
            return [None]*n_periods, [None]*n_periods, [None]*n_periods, [None]*n_periods, [None]*n_periods, [None]*n_periods
        PVI = np.zeros(shape=n_periods, dtype=float)
        NVI = np.zeros(shape=n_periods, dtype=float)
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
        PVI *= 1000/np.max(PVI)
        NVI *= 1000/np.max(NVI)
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
        if type(data_series) in [pd.Series, pd.DataFrame]:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        if any(data_series==None):
            return [None]*n_periods
        if n_periods<self.periods:
            return [None] * n_periods
        elif n_periods == self.periods:
            return [None] * (self.periods-1) + [data_series.mean()]
        else:
            SMMA = np.zeros(shape=n_periods, dtype=float)
            for i in range(self.periods-1):
                SMMA[i] = None
            SMMA[self.periods-1] = data_series[:self.periods].mean()
            for idx in range(self.periods, n_periods):
                SMMA[idx] = ((self.periods-1)*SMMA[idx-1] + data_series[idx])/self.periods
            return SMMA

    def exponential(self, data_series: np.ndarray):
        if type(data_series) in [pd.Series, pd.DataFrame]:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        if any(data_series==None):
            return [None]*n_periods
        EMA = np.zeros(shape=n_periods, dtype=float)
        EMA[0] = data_series[0]
        for idx in range(1, n_periods):
            EMA[idx] = (data_series[idx] * self.multiplier) + (EMA[idx-1] * (1-self.multiplier))
        return EMA

    def simple(self, data_series: np.ndarray):
        if type(data_series) in [pd.Series, pd.DataFrame]:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        if any(data_series==None):
            return [None]*n_periods
        SMA = np.zeros(shape=n_periods, dtype=float)
        data = np.array(data_series)
        for idx in range(n_periods):
            if idx > (self.periods-1):
                SMA[idx] = np.mean(data[(idx-self.periods+1):(idx+1)])
            else:
                SMA[idx] = np.nan
        return SMA
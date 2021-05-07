# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import pandas as pd
import numpy as np

from ..math_and_stats import Cubic_Spline_Approximation_Smoothing

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


class trend_indicator(object):
    def __init__(self):
        super().__init__()

    def ADX(self, high_price: np.ndarray, 
                  low_price: np.ndarray,
                  close_price: np.ndarray,
                  ADX_smoothing_len: int = 14,
                  DI_len: int = 14):
        """
        Average Directional Index (ADX)
        https://www.investopedia.com/articles/trading/07/adx-trend-indicator.asp
        https://www.investopedia.com/terms/a/adx.asp

        DI = Directional Indicator (i.e., DMI+, DMI-)
        """
        if type(high_price) == pd.Series:
            high_price = high_price.to_numpy()
        if type(low_price) == pd.Series:
            low_price = low_price.to_numpy()
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        n_periods = close_price.shape[0]
        if n_periods <= 1:
            #raise ValueError(f"n_periods cannot be <= 1")
            return [None,], [None,], [None,], [None,], [None,], [None,], [None,], [None,]
        if (high_price.shape[0] != low_price.shape[0]) or (high_price.shape[0] != close_price.shape[0]) or (low_price.shape[0] != close_price.shape[0]):
            raise RuntimeError(f"The lengths of high_price [{high_price.shape[0]}], low_price [{low_price.shape[0]}], close_price [{close_price.shape[0]}] are different")
        higher_highs = list(np.diff(high_price))
        lower_lows = list(-np.diff(low_price))
        higher_highs.insert(0, None)
        lower_lows.insert(0, None)
        DM_plus = [None] * n_periods # Directional Movement
        DM_minus = [None] * n_periods
        TR = [None] * n_periods # True Range
        for idx in range(1, n_periods):
            if higher_highs[idx] > lower_lows[idx] and higher_highs[idx] > 0:
                DM_plus[idx] = higher_highs[idx]
            else:
                DM_plus[idx] = 0
            if lower_lows[idx] > higher_highs[idx] and lower_lows[idx] > 0:
                DM_minus[idx] = lower_lows[idx]
            else:
                DM_minus[idx] = 0
            TR[idx] = max(high_price[idx]-low_price[idx],
                          high_price[idx]-close_price[idx-1],
                          low_price[idx]-close_price[idx-1])
        TR_rma = moving_average(periods = DI_len).rma(data_series = np.array(TR[1:]))
        TR_rma[TR_rma == 0] = np.nan
        plus = 100 * moving_average(periods = DI_len).rma(data_series = np.array(DM_plus[1:])) / TR_rma
        minus = 100 * moving_average(periods = DI_len).rma(data_series = np.array(DM_minus[1:])) / TR_rma
        plus_and_minus = plus + minus
        adx = abs(plus - minus)
        for idx in range(n_periods-1):
            if plus_and_minus[idx] != 0:
                adx[idx] /= plus_and_minus[idx]
        adx *= 100
        adx_smoothed = moving_average(periods = ADX_smoothing_len).rma(data_series = adx)
        plus_smoothed = moving_average(periods = ADX_smoothing_len).rma(data_series = plus)
        minus_smoothed = moving_average(periods = ADX_smoothing_len).rma(data_series = minus)
        # spline smoothed
        if len(adx) == 0:
            trend = trend_short = []
        elif len(adx) == 1:
            trend = trend_short = [None,]
        else:
            x = np.arange(len(adx))
            adx_smooth = 0.90
            adx_csaps, adx_smooth = Cubic_Spline_Approximation_Smoothing(x=x, y=adx, smooth=adx_smooth)            
            #
            trend = [None] * (n_periods-1)
            trend_short = [None] * (n_periods-1)
            for idx in range(len(adx)):
                adx_slope = ''
                adx_slope_short = ''
                trend_strength = ''
                trend_strength_short = ''
                trend_direction = ''
                trend_direction_short = ''
                #
                if idx > 0:
                    if adx_csaps[idx] > adx_csaps[idx-1]:
                        adx_slope = 'continued' # increasing
                        adx_slope_short = 'c.'
                    elif adx_csaps[idx] == adx_csaps[idx-1]:
                        adx_slope = 'unchanged' # unchanged
                        adx_slope_short = 'u.'
                    else:
                        adx_slope = 'faded' # decreasing
                        adx_slope_short = 'f.'
                #
                if adx_csaps[idx] < 20:
                    trend_strength = 'weak'
                    trend_strength_short = 'w.'
                elif 20 <= adx_csaps[idx] and adx_csaps[idx] <= 40:
                    trend_strength = 'moderate'
                    trend_strength_short = 'm.'
                elif 40 < adx_csaps[idx]:
                    trend_strength = 'strong'
                    trend_strength_short = 's.'
                #
                if plus[idx] > minus[idx]:
                    trend_direction = 'uptrend'
                    trend_direction_short = 'up.'
                elif plus[idx] < minus[idx]:
                    trend_direction = 'downtrend'
                    trend_direction_short = 'dn.'
                else:
                    trend_direction = 'nd-trend'
                    trend_direction_short = 'nt.'
                trend[idx] = f"{adx_slope} {trend_strength} {trend_direction}"
                trend_short[idx] = f"{adx_slope_short}{trend_strength_short}{trend_direction_short}"
            #
        #for debugging
        #print(f"adx={adx}, plus={plus}, minus={minus}, adx_smoothed={adx_smoothed}, plus_smoothed={plus_smoothed}, minus_smoothed={minus_smoothed}, trend={trend}, trend_short={trend_short}")
        return [None] + list(adx), [None] + list(plus), [None] + list(minus), [None] + list(adx_smoothed), [None] + list(plus_smoothed), [None] + list(minus_smoothed), [None] + trend, [None] + trend_short

    """
    def trends(self, high_price: np.ndarray, low_price: np.ndarray, close_price: np.ndarray,):
        # Work in Progress
        ADX, Plus, Minus, ADX14, Plus14, Minus14 = self.ADX(high_price = high_price, low_price = low_price, close_price = close_price)
        for 
        if type(typical_price) == pd.Series:
            typical_price = typical_price.to_numpy()
        n_periods = typical_price.shape[0]
        if n_periods == 0:
            raise ValueError(f"n_periods cannot be zero")
        EMA = moving_average(periods = n_smoothing_periods).exponential(data_series = typical_price)
        distance_scalar = (EMA.max() - EMA.min()) / EMA.size
        if EMA.size >= 3: # to calculate a numerical gradient, at least (edge_order + 1) elements are required.
            EMA_grad = np.gradient(EMA, distance_scalar, edge_order=2)
        else:
            EMA_grad = None
    """


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
            elif (up[i] is None) or (down[i] is None):
                RSI[i] = None
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
        if n_periods > periods:
            for today_idx in range(periods):
                MFI[today_idx] = None
            for today_idx in range(periods, n_periods):
                for idx in range(periods):
                    if typical_price[today_idx-idx] > typical_price[today_idx-idx-1]:
                        positive_money_flow[today_idx] += money_flow[today_idx-idx]
                    elif typical_price[today_idx-idx] < typical_price[today_idx-idx-1]:
                        negative_money_flow[today_idx] += money_flow[today_idx-idx]
                MFI[today_idx] = 100 * positive_money_flow[today_idx] / (positive_money_flow[today_idx]+negative_money_flow[today_idx])
        else:
            for today_idx in range(n_periods):
                MFI[today_idx] = None
        return MFI
        
    def PPO(self, close_price: np.ndarray, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        https://www.investopedia.com/terms/p/ppo.asp
        """
        if type(close_price) == pd.Series:
            close_price = close_price.to_numpy()
        fast_EMA = moving_average(periods=fast_period).exponential(close_price)
        slow_EMA = moving_average(periods=slow_period).exponential(close_price)
        ppo = 100 * (fast_EMA - slow_EMA) / slow_EMA # the only thing that differs vs. MACD
        signal = moving_average(periods=signal_period).exponential(ppo)
        histogram = ppo - signal
        return ppo, signal, histogram            

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
            if high_price[today_idx] == low_price[today_idx]:
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

    def rma(self, data_series: np.ndarray):
        """
        see rma in https://www.tradingview.com/pine-script-reference/
        """
        return np.array(self.exponential(data_series = data_series, use_default_alpha = False, alpha = 1 / self.periods))

    def exponential(self, data_series: np.ndarray, use_default_alpha: bool = True, alpha = None):
        if use_default_alpha:
            alpha = self.multiplier
        if type(data_series) in [pd.Series, pd.DataFrame]:
            data_series = data_series.to_numpy()
        n_periods = data_series.shape[0]
        if any(data_series==None):
            return [None]*n_periods
        EMA = np.zeros(shape=n_periods, dtype=float)
        EMA[0] = data_series[0]
        for idx in range(1, n_periods):
            EMA[idx] = (data_series[idx] * alpha) + (EMA[idx-1] * (1-alpha))
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
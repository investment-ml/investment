# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0


import numpy as np
from scipy.stats import norm


class probability:
    def p_A_given_B(self, p_B_given_A, p_A, p_B):
        """
        P(A|B) = P(B|A)*P(A)/P(B)
        """
        p_A_and_B = p_B_given_A * p_A
        return p_A_and_B / p_B


class volatility:

    """
    implied volatility
    # to try: https://pypi.org/project/py-vollib-vectorized/

    # https://www.fidelity.com/viewpoints/active-investor/implied-volatility
    https://www.investopedia.com/terms/b/blackscholes.asp
    https://www.investopedia.com/terms/i/iv.asp
    https://www.investopedia.com/trading/using-the-greeks-to-understand-options/
    https://www.investopedia.com/articles/optioninvestor/08/implied-volatility.asp
    """

    # https://stackoverflow.com/questions/61289020/fast-implied-volatility-calculation-in-python

    N = norm.cdf

    # Black-Scholes formula
    def bs_call(self, S, K, T, r, vol):
        """
        vol: implied volatility
        """
        d1 = (np.log(S/K) + (r + 0.5*vol**2)*T) / (vol*np.sqrt(T))
        d2 = d1 - vol * np.sqrt(T)
        return S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)

    def bs_vega(self, S, K, T, r, sigma):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return S * norm.pdf(d1) * np.sqrt(T)

    def implied_volatility(self, call_price, S, K, T, r, *args):
        """
        https://www.investopedia.com/terms/b/blackscholes.asp
        call_price = call option price (premium/share)
        S = current stock price
        K = strike price
        T = Time to maturity
        r = risk-free interest rate
        """
        MAX_ITERATIONS = 200
        PRECISION = 1.0e-5
        sigma = 0.5
        for i in range(0, MAX_ITERATIONS):
            price = self.bs_call(S, K, T, r, sigma)
            vega = self.bs_vega(S, K, T, r, sigma)
            diff = call_price - price  # our root
            if (abs(diff) < PRECISION):
                return sigma
            sigma = sigma + diff/vega # f(x) / f'(x)
        return sigma # value wasn't found, return best guess so far
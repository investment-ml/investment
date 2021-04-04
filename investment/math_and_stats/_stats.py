# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0

import math
from scipy.special import expit
from scipy.stats import norm, chisquare
import statsmodels.api as sm
from csaps import csaps

def sigmoid(z):
    return expit(z) # 1.0 / (1.0 + np.exp(-z)) # to cope with the overflow problem with np.exp()

def p_value_for_z_score(z, sided=2):
    return sided * (1 - norm.cdf(abs(z)))

def z_score_for_p_value(p, sided=2):
    return norm.ppf(1 - p/sided)

def one_sample_proportion_z_test(p, p0, n):
    """
    Example: p=23/124=0.19
    Question: H0: p=0.07
    one_sample_proportion_z_test(0.19, 0.07, 124)
    """
    z = (p-p0) / math.sqrt(p0*(1-p0)/n)
    p_value = p_value_for_z_score(z)
    CI = z_score_for_p_value(0.05)*math.sqrt(p*(1-p)/n)
    print(f"H0: {p:.2f} = {p0:.2f} ==> z = {z:.4f}, p-value = {p_value:.5f}, 95% C.I. of proportion = {p:.2f} = ({p-CI:.2f}, {p+CI:.2f})\n")

def two_sample_proportion_z_test(num1, num2, denom1, denom2):
    """
    Example: p1 = 41/195, p2 = 351/605
    two_proportion_z_test(41, 351, 195, 605): Z = -8.99, p < .0001
    """
    p = (num1+num2) / (denom1+denom2)
    p1 = num1/denom1
    p2 = num2/denom2
    z = ((p1-p2)-0) / math.sqrt(p*(1-p)*(1/denom1+1/denom2))
    p_value = p_value_for_z_score(z)
    print(f'z = {z:.4f}, p = {p_value:.5f}')

def chisq_test(num1, num2):
    return chisquare([num1, num2])

def Locally_Weighted_Scatterplot_Smoothing(y, x, frac):
    """
    https://www.statsmodels.org/stable/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html?highlight=lowess
    https://stackoverflow.com/questions/36252434/predicting-on-new-data-using-locally-weighted-regression-loess-lowesspip
    https://www.displayr.com/how-to-add-trend-lines-in-r-using-plotly/
    """
    lowess = sm.nonparametric.lowess(endog=y, exog=x, frac=frac)
    lowess_y = list(zip(*lowess))[1]
    lowess_x = list(zip(*lowess))[0]
    return lowess_y, lowess_x

def Cubic_Spline_Approximation_Smoothing(y, x, smooth = None):
    xi = x # i = interpolation
    if smooth is None:
        y_csaps, smooth = csaps(x, y, xi)
    else:
        y_csaps = csaps(x, y, xi, smooth=smooth)
    return y_csaps, smooth

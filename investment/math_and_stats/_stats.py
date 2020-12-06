# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL

from scipy.special import expit

def sigmoid(z):
    return expit(z) # 1.0 / (1.0 + np.exp(-z)) # to cope with the overflow problem with np.exp()
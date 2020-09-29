# -*- coding: utf-8 -*-

# Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
# License: BSD 3 clause

from investment.data import pull_data
data = pull_data()

import matplotlib.pyplot as plt
data.Close.plot()
plt.show()

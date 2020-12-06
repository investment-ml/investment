# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL

class probability:
    def p_A_given_B(self, p_B_given_A, p_A, p_B):
        """
        P(A|B) = P(B|A)*P(A)/P(B)
        """
        p_A_and_B = p_B_given_A * p_A
        return p_A_and_B / p_B

.. -*- mode: rst -*-

|BuildTest|_ |PyPi|_ |License|_ |Downloads|_ |PythonVersion|_

.. |BuildTest| image:: https://travis-ci.com/investment-ml/investment.svg?branch=master
.. _BuildTest: https://travis-ci.com/github/investment-ml/investment

.. |PyPi| image:: https://img.shields.io/pypi/v/investment
.. _PyPi: https://pypi.python.org/pypi/investment

.. |License| image:: https://img.shields.io/pypi/l/investment
.. _License: https://pypi.python.org/pypi/investment

.. |Downloads| image:: https://pepy.tech/badge/investment
.. _Downloads: https://pepy.tech/project/investment

.. |PythonVersion| image:: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue
.. _PythonVersion: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue


===========================
A Python App for Investment
===========================

Features
-------------------
- 9000+ tickers as included in major indexes and exchanges (DOW 30, NASDAQ 100, S&P 500, Russell 2000, ARK investment, etc.)
- Breakdown by 11 sectors and 145 industries; key info for each ticker; Common indicators: ADX, RSI, Money Flow, OBV, A/D, MACD, PPO, PVI/NVI, Bollinger Bands
- An ETF database of 2000+ tickers, and an equity database of 7000+ tickers


Install and Execute
-------------------


.. code-block:: bash

   $ python -m venv env        # the binary may be called 'python3'
   $ source env/bin/activate   # for Linux and macOS
   $ env\Scripts\activate.bat  # for Windows 
   $ pip install investment    # this only needs to be done once
   $ python -m investment      # after installation, execute within the virtual environment (recommended)

   # Note: to obtain price target, package 'selenium' and a Chrome browser driver must be installed on your computer first
   # see https://pypi.org/project/selenium/

   
Sample Screenshot
-----------------
|image_UBER|


.. |image_UBER| image:: https://github.com/investment-ml/investment/raw/master/examples/gui/images/UBER.png

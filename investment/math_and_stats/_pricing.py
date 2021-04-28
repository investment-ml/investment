# -*- coding: utf-8 -*-

#  Author: Investment Prediction Enthusiast <investment.ml.prediction@gmail.com>
#
#  License: LGPL-3.0


import numpy as np
from scipy.stats import norm


class pricing_demo:
    def option(self):
        
        # Option
        strike_price = 310
        time_to_maturity = 14 / 365.25 # this must be accurate to the millisecond, including the expiration time is at 11:59am on the expiration date, as the B-S formula assumes continuous compound interest
        # https://www.investopedia.com/terms/e/expiration-time.asp
        # https://www.nasdaq.com/glossary/e/expiration-time
        # "The time of day by which all exercise notices must be received on the expiration date. 
        # Technically, the expiration time is currently 11:59 a.m. [Eastern Time] on the expiration date, but public holders of option contracts must indicate their desire to exercise no later than 5:30 p.m. [Eastern Time] on the business day preceding the expiration date."
        
        # Stock
        curr_stock_price = 301.13 # spot price
        expected_volatility_pct = 40.95 # (%)
        expected_dividend_pct = 0
        
        # Market
        expected_risk_free_interest_rate = 1.5595 # (%), United States 10-Year Bond Yield
        
        # Calculation
        this_bs = Black_Scholes(strike_price = strike_price, time_to_maturity = time_to_maturity,
                                curr_stock_price = curr_stock_price, expected_volatility_pct = expected_volatility_pct, expected_dividend_pct = expected_dividend_pct,
                                expected_risk_free_interest_rate = expected_risk_free_interest_rate)
        print(f"While the current price of $XYZ in the marketplace is ${curr_stock_price:.2f} on 2021-04-23, regarding 1 call contract $XYZ 2021-05-07 strike ${strike_price:.2f}.")
        print(f"According to the Black-Scholes model, the present premium is [${this_bs.present_value_of_call_option_price:.2f}/share], and the ask (or bid) price should be higher (or lower) than that.")
        #
        strike_price = 292.5
        expected_volatility_pct = 42.04 # (%)
        this_bs = Black_Scholes(strike_price = strike_price, time_to_maturity = time_to_maturity,
                                curr_stock_price = curr_stock_price, expected_volatility_pct = expected_volatility_pct, expected_dividend_pct = expected_dividend_pct,
                                expected_risk_free_interest_rate = expected_risk_free_interest_rate)
        print(f"While the current price of $XYZ in the marketplace is ${curr_stock_price:.2f} on 2021-04-23, regarding 1 put contract $XYZ 2021-05-07 strike ${strike_price:.2f}.")
        print(f"According to the Black-Scholes model, the present premium is [${this_bs.present_value_of_put_option_price:.2f}/share], and the ask (or bid) price should be higher (or lower) than that.")


class Black_Scholes:
    """
    references: 
    1. https://www.math.drexel.edu/~pg/fin/VanillaCalculator.html
    2. https://medium.com/magnimetrics/black-scholes-model-first-steps-bdcbe1691da7 (this one includes dividends)
    3. http://socr.ucla.edu/htmls/HTML5/econ_apps/BlackScholesPlot/BlackScholesPlot.html (graphics)
    4. https://brilliant.org/wiki/black-scholes-merton/ (some explanation)
    5. https://www.investopedia.com/terms/b/blackscholes.asp
    """

    ############################################
    
    def __init__(self, strike_price: float = None, time_to_maturity: float = None, # Option
                       curr_stock_price: float = None, expected_volatility_pct: float = None, expected_dividend_pct: float = 0, # Stock
                       expected_risk_free_interest_rate: float = None): # Market
        """
        Option, Stock, Market
        """
        # Option
        self.K_at_maturity = strike_price
        self.t = time_to_maturity # one year will be t=1
        # Stock
        self.S_at_maturity = curr_stock_price # the spot price, which is also the assumed price of the underlying asset at expiration
        self.sigma = expected_volatility_pct / 100
        self.q = expected_dividend_pct / 100 # e.g., $XOM dividend yield is 6.29%, then self.q = 0.0629
        # Market
        self.r = expected_risk_free_interest_rate / 100 # APY, e.g., U.S. 10-Year Bond Yield = 1.5595%, then self.r = 0.015595
        #
        self.rv = norm()

    ############################################

    @property
    def present_value_of_strike_price(self):
        """
        the exercise (strike) price discounted back to present value.

        This is calculating K_now, while considering capital appreciation of strike price due to [risk-free interest] before expiration, and now means present.

        At maturity, the strike price is K;
        At present, the value of the strike price is K_now, which is always ≤ K, but K_now will grow into K via continuous compound [interest];
        The reason is because from present to maturity, the call strike price will undergo capital appreciation via [risk-free interest], so that K_now will grow into K at then.

        To understand why it involves exponential:

        let's say n = # of times per year [interest] is compounded;
        If the [interest] is compounded only once per year (n=1), then K = K_now * (1+r)^t;

        But if [interest] is compounded continually (n -> ∞), then K = K_now * e^rt;

        That is why K_now = K / e^rt = K * e^-rt
        """
        return self.K_at_maturity * np.exp(-self.r*self.t)
        
    @property
    def present_value_of_stock_price(self):
        """
        the stock price discounted back to present value.

        This is calculating S_now, while considering capital appreciation of stock price due to [dividend] before expiration, and now means present.

        At maturity, the stock price is assumed to be the same as the spot price;
        At present, the value of the stock price is S_now, which is always ≤ S, but S_now will grow into S via continuous compound [dividend]; 
        The reason is because from present to maturity, the stock price will undergo capital appreciation via [dividend], so that S_now will grow into S.

        To understand why it involves exponential:

        let's say n = # of times per year [dividend] is compounded;
        If the [dividend] is compounded only once per year (n=1), then S = S_now * (1+q)^t;

        But if [dividend] is compounded continually (n -> ∞), then S = S_now * e^qt;

        That is why S_now = S / e^qt = S * e^-qt
        """
        return self.S_at_maturity * np.exp(-self.q*self.t)

    ############################################

    @property
    def normalizing_factor(self):
        """
        https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1682261_code140767.pdf?abstractid=1682261&mirid=1

        this is the SD of the normal distribution.
        """
        return self.sigma * (self.t**0.5)

    ################# for call #################

    @property
    def d_center_for_call(self):
        """
        the ratio of [the present value of the stock price] over [the present value of the strike price];
        recall that ln(1) = 0, ln(>1) > 0, ln(<1) < 0;
        if stock = strike, d_center = 0;
        if stock > strike at present (thus more likely ITM at maturity for call), d_center_for_call > 0;
        if stock < strike at present (thus more likely OTM at maturity for call), d_center_for_call < 0;
        
        d_center_for_call is assumed to be normally distributed.

        The Black-Scholes model posits that stock shares will have a lognormal distribution of prices, following a random walk with constant drift and volatility.
        """
        return np.log(self.present_value_of_stock_price / self.present_value_of_strike_price) / self.normalizing_factor

    # note that (+d1) - (+d2) = 1 SD

    @property
    def positive_d1_for_call(self):
        """
        https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1682261_code140767.pdf?abstractid=1682261&mirid=1
        +d1: 0.5 SD [above, thus favoring the call buyer] the d_center_for_call in a normal distribution of d_center_for_call;
        +d1: the asymmetry in option payoff that favors the call buyer (higher intrinsic value);

        why 0.5 SD? This is to ensure that the current intrinsic value of the call option won't be negative.
        """
        #return (np.log(self.S/self.K) + (self.r - self.q + ((self.sigma**2)/2)) * self.t) / (self.sigma * (self.t**0.5))
        return self.d_center_for_call + (0.5*self.normalizing_factor)

    @property
    def positive_d2_for_call(self):
        """
        https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1682261_code140767.pdf?abstractid=1682261&mirid=1
        +d2: 0.5 SD [below, thus favoring the call seller] the d_center_for_call in a normal distribution of d_center_for_call
        +d2: the asymmetry in option payoff that favors the call seller (lower intrinsic value);

        why 0.5 SD? This is to ensure that the current intrinsic value of the call option won't be negative.
        """
        # return self.d1 - (self.sigma * (self.t**0.5))
        #return (np.log(self.S/self.K) + (self.r - self.q - ((self.sigma**2)/2)) * self.t) / (self.sigma * (self.t**0.5))
        return self.d_center_for_call - (0.5*self.normalizing_factor)

    @property
    def N_positive_d1_for_call(self):
        """
        https://quant.stackexchange.com/questions/46856/where-can-i-find-a-clear-explanation-brief-derivation-of-nd1-and-nd2
        # after favoring the call buyer, the risk-adjusted probability of the call option finishing ITM and being exercised at maturity (the stock price > the strike price); range = 0 ~ 1; prob > 0.5 means more likely ITM; prob ≤ 0.5 means more likely OTM;
        # the risks here include (a) the risk-free interest, (b) the dividend, (c) the volatility, (d) the time to maturity.
        """
        return self.rv.cdf(self.positive_d1_for_call)

    @property
    def N_positive_d2_for_call(self):
        """
        https://quant.stackexchange.com/questions/46856/where-can-i-find-a-clear-explanation-brief-derivation-of-nd1-and-nd2
        # after favoring the call seller, the risk-adjusted probability of the call option finishing ITM and being exercised at maturity (the stock price > the strike price); range = 0 ~ 1; prob > 0.5 means more likely ITM; prob ≤ 0.5 means more likely OTM;
        # the risks here include (a) the risk-free interest, (b) the dividend, (c) the volatility, (d) the time to maturity.
        """
        return self.rv.cdf(self.positive_d2_for_call)

    @property
    def present_value_of_call_option_price(self):
        """
        meaning: the premium at present, the current intrinsic value of the call option (the part where stock > strike);
        at maturity, [call buyer]  expects the stock price > the strike price;
        at maturity, [call seller] expects the stock price ≤ the strike price;
        
        the result is always ≥ 0; the result will never be negative.
        when present_value_of_stock_price < present_value_of_strike_price, then both [probability_of_ITM_favoring_call_buyer] and [probability_of_ITM_favoring_call_seller] approach zero, making the result close to zero.
        """
        probability_of_ITM_favoring_call_buyer  = self.N_positive_d1_for_call
        probability_of_ITM_favoring_call_seller = self.N_positive_d2_for_call
        # assuming a person buy-to-open a call to take advantage of an uptrend
        the_expected_asset_value_as_selling_at_maturity = self.present_value_of_stock_price * probability_of_ITM_favoring_call_buyer # the amount that will likely be received on selling the stock at expiration
        the_expected_cash_cost_as_buying_at_maturity = self.present_value_of_strike_price * probability_of_ITM_favoring_call_seller # the payment (cost basis) that will likely be made to call away the stock from the seller when the call option is exercised at expiration
        return the_expected_asset_value_as_selling_at_maturity - the_expected_cash_cost_as_buying_at_maturity

    ################# for put #################

    @property
    def d_center_for_put(self):
        """
        the ratio of [the present value of the strike price] over [the present value of the stock price];
        recall that ln(1) = 0, ln(>1) > 0, ln(<1) < 0;
        if strike = stock, d_center = 0;
        if strike > stock at present (more likely ITM at maturity for put), d_center_for_put > 0;
        if strike < stock at present (more likely OTM at maturity for put), d_center_for_put < 0;
        
        d_center_for_put is assumed to be normally distributed.

        The Black-Scholes model posits that stock shares will have a lognormal distribution of prices, following a random walk with constant drift and volatility.
        """
        return np.log(self.present_value_of_strike_price / self.present_value_of_stock_price) / self.normalizing_factor

    # note that (-d2) - (-d1) = 1 SD

    @property
    def negative_d2_for_put(self):
        """
        https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1682261_code140767.pdf?abstractid=1682261&mirid=1
        -d2: 0.5 SD [above, thus favoring the put buyer] the d_center_for_put in a normal distribution of d_center_for_put;
        -d2: the asymmetry in option payoff that favors the put buyer (higher intrinsic value);
        """
        return self.d_center_for_put + (0.5*self.normalizing_factor)

    @property
    def negative_d1_for_put(self):
        """
        https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1682261_code140767.pdf?abstractid=1682261&mirid=1
        -d1: 0.5 SD [below, thus favoring the put seller] the d_center_for_put in a normal distribution of d_center_for_put;
        -d1: the asymmetry in option payoff that favors the put seller (lower intrinsic value);
        """
        return self.d_center_for_put - (0.5*self.normalizing_factor)

    @property
    def N_negative_d2_for_put(self):
        """
        # after favoring the put buyer, the risk-adjusted probability of the put option finishing ITM and being exercised at maturity (the strike price > the stock price); range = 0 ~ 1; prob > 0.5 means more likely ITM; prob ≤ 0.5 means more likely OTM;
        # the risks here include (a) the risk-free interest, (b) the dividend, (c) the volatility, (d) the time to maturity.
        """
        return self.rv.cdf(self.negative_d2_for_put)

    @property
    def N_negative_d1_for_put(self):
        """
        # after favoring the put seller, the risk-adjusted probability of the put option finishing ITM and being exercised at maturity (the strike price > the stock price); range = 0 ~ 1; prob > 0.5 means more likely ITM; prob ≤ 0.5 means more likely OTM;
        # the risks here include (a) the risk-free interest, (b) the dividend, (c) the volatility, (d) the time to maturity.
        """
        return self.rv.cdf(self.negative_d1_for_put)

    @property
    def present_value_of_put_option_price(self):
        """
        meaning: the premium at present, the current intrinsic value of the put option (the part where stock < strike);
        at maturity, [put buyer]  expects the stock price < the strike price;
        at maturity, [put seller] expects the stock price ≥ the strike price; 
        
        the result is always ≥ 0; the result will never be negative.
        when present_value_of_strike_price < present_value_of_stock_price, then both [probability_of_ITM_favoring_call_buyer] and [probability_of_ITM_favoring_call_seller] approach zero, making the result close to zero.
        """
        probability_of_ITM_favoring_put_buyer  = self.N_negative_d2_for_put
        probability_of_ITM_favoring_put_seller = self.N_negative_d1_for_put
        # assuming a person buy-to-open a put to take advantage of a downtrend
        the_expected_cash_value_as_short_selling_at_maturity = self.present_value_of_strike_price * probability_of_ITM_favoring_put_buyer
        the_expected_asset_cost_as_buying_cover_at_maturity = self.present_value_of_stock_price * probability_of_ITM_favoring_put_seller
        return the_expected_cash_value_as_short_selling_at_maturity - the_expected_asset_cost_as_buying_cover_at_maturity


class Bjerksund_Stensland:
    """
    references:
    1. https://www.investopedia.com/terms/b/bjerksundstensland-model.asp
    """
    def __init__(self):
        pass

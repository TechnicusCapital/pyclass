import argparse
import datetime
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt

# ---- CONSTANTS
START = '2020-01-01'
END = '2023-07-01'
TICKERS = ['TSLA', 'AMD']

# ---- TICKER CLASS FOR HOLDING STATIC DATA
class Ticker: 
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker
        self.data = yf.download(self.ticker, start=START, end=END)
        self.close = self.data.Close
        self.open = self.data.Open
        self.high = self.data.High
        self.low = self.data.Low

# ---- STRATEGY CLASS FOR SIGNAL GENERATION
class Strategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        # self.open = data['Open']
        # self.high = data['High']
        # self.low = data['Low']
        self.close = self.data.Close
        self.side = int()
        self.rsi = pd.Series(dtype='float64')

    def static_crossover(self, indicator: pd.Series, level):
        if indicator[len(indicator) - 1] > level and indicator[len(indicator) - 2] < level:
            return True
        
    def static_crossunder(self, indicator: pd.Series, level):
        if indicator[len(indicator) - 1] < level and indicator[len(indicator) - 2] > level:
            return True

    def dynamic_cross(self, src1, direction: int, src2):
        if direction == 1:
            if src1[self.idx] > src2[self.idx] and src1[self.idx - 1] < src2[self.idx - 1]:
                return True
            else:
                return False
        elif direction == -1:
            if src1[self.idx] < src2[self.idx] and src1[self.idx - 1] > src2[self.idx - 1]:
                return True
            else:
                return False
    
    def current_signal(self):
        # -- Trade Logic Goes Here
        # - This is an example of a long/short RSI strategy
        self.rsi = ta.rsi(self.close, 14)
        if self.rsi.tail(1).values[-1] > 50:
            self.side = 1
            return self.side
        elif self.rsi.tail(1).values[-1] < 50:
            self.side = -1
            return self.side
        # elif self.side != 0 and rsi[len(rsi) - 1] > 30 or rsi[len(rsi) - 1] < 70:
        #     self.side = 0
        #     return self.side
        else: 
            return self.side
        
    def last_signal(self):
        # -- Trade Logic Goes Here
        # - This is an example of a long/short RSI strategy
        rsi = ta.rsi(self.close, 14)
        self.data['rsi'] = rsi
        if rsi[len(rsi) - 2] > 70 and rsi[len(rsi) - 3] < 70:
            self.side = 1
            return self.side
        elif rsi[len(rsi) - 2] < 30 and rsi[len(rsi) - 3] > 30:
            self.side = -1
            return self.side
        else:
            return self.side

# ---- TRADE CLASS FOR HOLDING TRADE DATA
class Trade:
    def __init__(self, ticker: str, id: int, type: str, size: int, entry_idx: int):
        self.ticker = ticker
        self.id = id
        self.type = type
        self.prices = pd.Series(dtype='float64')
        self.size = size
        self.entry_idx = entry_idx
        self.exit_idx = int()
        self.profit = int()
        self.entry = int()
        self.exit = int()
    
    # -- USE FIRST AND LAST PRICE TO CALCULATE TRADE PROFIT
    def pnl(self):
        if len(self.prices) > 0:
            self.exit = self.prices.iloc[-1]
            self.entry = self.prices.iloc[0]
            self.profit = (self.exit - self.entry) * self.size
        else:
            self.profit = 0
        return self.profit

    def intertrade_prices(self):
        return self.prices

# ---- BACKTEST CLASS FOR TESTING A STRATEGY
class Backtest:
    def __init__(self, ticker: Ticker):
        self.ticker = ticker
        self.data = pd.DataFrame()
        self.initial_equity = 100
        self.data['equity'] = self.initial_equity
        self.data['position'] = 0
        self.idx = 0
        self.position = 0
        self.trades = 0
        self.trade_list = []

    def buy(self):
        self.data.position[self.idx] = 1
        self.position = 1
        self.trade_list.append(Trade(self.ticker, self.trades, 'LONG', 1, self.idx))
        #print(f'buy @ ${self.data.Close[self.idx]} on bar {self.idx}')

    def sell(self):
        self.data.position[self.idx] = -1
        self.position = -1
        self.trade_list.append(Trade(self.ticker, self.trades, 'SHORT', -1, self.idx))
        #print(f'sell @ ${self.data.Close[self.idx]} on bar {self.idx}')

    def flat(self):
        self.data.position[self.idx] = 0
        self.position = 0
        open_trade = self.trade_list[self.trades - 1]
        open_trade.prices = self.data.Close[open_trade.entry_idx:self.idx+1]
        open_trade.exit_idx = self.idx
        #print(f'flat @ ${self.data.Close[self.idx]} on bar {self.idx}')




    def update_eq(self):
        if self.data.position[self.idx - 1] != 0 and self.position == 0:
            last_trade = self.trade_list[self.trades - 1]
            self.data.equity[self.idx] = self.data.equity[last_trade.entry_idx] + last_trade.pnl()
            #print(f'Trade Closed with ${last_trade.pnl()} profit on bar {self.idx}')
        elif self.data.position[self.idx - 1] != 0 and self.position != 0:
            open_trade = self.trade_list[self.trades - 1]
            self.data.equity[self.idx] = self.data.equity[self.idx - 1] + ((self.data.Close[self.idx] - self.data.Close[self.idx - 1]) * self.position)
        else:
            self.data.equity[self.idx] = self.data.equity[self.idx - 1]

    def backtest(self):
        print(f'Beginning backtest with ${self.initial_equity}')
        for price in self.ticker.data.Close:
            self.data = pd.concat([self.data, pd.DataFrame({'Close': [price]})], ignore_index=True)
            if self.idx == 0:
                self.data.position[self.idx] = 0
                # self.data.returns[self.idx] = 1
                self.data.equity[self.idx] = self.initial_equity
                self.idx += 1
                continue

            self.data.position[self.idx] = self.data.position[self.idx - 1]

            if len(self.data) > 50:
                self.strategy = Strategy(self.data)
                if self.strategy.current_signal() == 1:
                    if self.data.position[self.idx - 1] != 0:
                        self.flat()
                    self.trades += 1
                    self.buy()
                if self.strategy.current_signal() == -1 and self.data.position[self.idx - 1] != 0:
                    if self.data.position[self.idx - 1] != 0:
                        self.flat()
                    self.trades += 1
                    self.sell()
                if self.strategy.current_signal() == 0 and self.data.position[self.idx - 1] != 0:
                    self.flat()
                print(self.data.equity[self.idx], self.strategy.rsi.tail(1).values[0] ,self.strategy.side, self.data.Close[self.idx], self.idx)
            self.update_eq()
            print(self.data.equity[self.idx])
            self.idx += 1

        return self.trade_list, self.data.Close, self.data.equity
    
    def stats(self):
        wins = 0
        for trade in self.trade_list:
            wins += 1 if trade.pnl() > 0.00 else 0
        print(f'Initial Equity: ${self.initial_equity}\n \
              Final Equity: ${self.data.equity[len(self.data.equity) - 1]}\n \
              Total Trades: {len(self.trade_list)}\n \
              Return: {round((self.data.equity[len(self.data.equity) - 1] - self.initial_equity) / self.initial_equity * 100, 2)}%\n \
              Winrate: {round(wins / len(self.trade_list) * 100, 2)}%\n \
              Average Profit: ${sum(trade.pnl() for trade in self.trade_list) / len(self.trade_list)}')
                    

amd = Ticker('AAPL')

test = Backtest(amd)

trades, prices, equity = test.backtest()

import timeit

# def run_backtest():
#     trades, prices, equity = test.backtest()
#     test.stats()

# execution_time = timeit.timeit(run_backtest, number=1)
# print(f"Execution time: {execution_time} seconds")

# print(prices)
# test.stats()

prices.plot()
equity.plot()
plt.show()
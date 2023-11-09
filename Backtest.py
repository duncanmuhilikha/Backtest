# Ignore printing all warnings
#warnings.filterwarnings('ignore')

# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import pyfolio as pf
import datetime as dt
import pandas_datareader.data as web
import os
import warnings
warnings.filterwarnings("ignore")
# print all outputs
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"



# Define a list of tickers for the assets to download
tickers = ['AAPL', 'GOOG', 'TSLA', 'MSFT', 'AMZN', 'FB', 'NVDA', 'PYPL', 'NFLX', 'ADBE', 'CRM', 'ASML', 'NKE', 'ORCL', 'CSCO', 'INTC', 'PEP', 'ABT', 'AVGO', 'QCOM', 'TXN', 'ACN', 'MMM', 'KO', 'PFE', 'PG', 'HD', 'UNH', 'JNJ', 'MA', 'BAC', 'V', 'JPM', 'WMT', 'DIS', 'VZ', 'CVX', 'XOM', 'CAT', 'BA', 'MCD', 'GS', 'IBM', 'MRK', 'WFC', 'C', 'RTX', 'AXP', 'SPY']

# Download the data for each ticker
data = {}
for ticker in tickers:
    data[ticker] = yf.download(ticker)

# Concatenate the data for all tickers into a single DataFrame
all_data = pd.concat(data.values(), keys=data.keys())

# Drop rows with missing values
all_data.dropna(inplace=True)

# Keep only the Adj Close column and rename it to the ticker symbol
all_data = all_data['Adj Close'].reset_index().pivot(index='Date', columns='level_0', values='Adj Close')
all_data.columns.name = None

# Select at least 100 assets
all_data = all_data.sample(n=max(100, len(tickers)), axis=1)

# Save the data to a CSV file
all_data.to_csv('financial_assets.csv')

all_data.head()
###Drop NaN
dat=all_data.dropna()

dat.head()
dat.describe()
import matplotlib.pyplot as plt

dat['AAPL'].plot()
plt.xlabel("Date")
plt.ylabel("Adjusted")
plt.title("Apple Price data")
plt.show()

###Returns
daily_returns = dat.pct_change()

import matplotlib.pyplot as plt

daily_returns['AAPL'].plot()
plt.xlabel("Date")
plt.ylabel("Apple returns")
plt.title("Apple daily stock returns")
plt.show()


daily_returns.head()
daily_returns.describe()
fig = plt.figure()
(daily_returns + 1).cumprod().plot()
plt.show()

# calculating buy and hold strategy returns
daily_returns = dat.pct_change()
daily_returns.head()


# creating bollinger band indicators
daily_returns['ma20'] = daily_returns['AAPL'].rolling(window=20).mean()
daily_returns['std'] = daily_returns['AAPL'].rolling(window=20).std()
daily_returns['upper_band'] = daily_returns['ma20'] + (2 * daily_returns['std'])
daily_returns['lower_band'] = daily_returns['ma20'] - (2 * daily_returns['std'])
daily_returns.drop(['Open','High','Low'],axis=1,inplace=True,errors='ignore')
daily_returns.tail(5)


# BUY condition
daily_returns['signal'] = np.where((daily_returns['AAPL'] < daily_returns['lower_band']) &
                        (daily_returns['AAPL'].shift(1) >=       daily_returns['lower_band']),1,0)

# SELL condition
daily_returns['signal'] = np.where( (daily_returns['AAPL'] > daily_returns['upper_band']) &
                          (daily_returns['AAPL'].shift(1) <= daily_returns['upper_band']),-1,daily_returns['signal'])
# creating long and short positions 
daily_returns['position'] = daily_returns['signal'].replace(to_replace=0, method='ffill')

# shifting by 1, to account of close price return calculations
daily_returns['position'] = daily_returns['position'].shift(1)

# calculating strategy returns
daily_returns['strategy_returns'] = daily_returns['AAPL'] * (daily_returns['position'])

daily_returns.tail(5)


# comparing buy & hold strategy / bollinger bands strategy returns
print("Buy and hold returns:",daily_returns['AAPL'].cumsum()[-1])
print("Strategy returns:",daily_returns['strategy_returns'].cumsum()[-1])

# plotting strategy historical performance over time
daily_returns[['AAPL','strategy_returns']] = daily_returns[['AAPL','strategy_returns']].cumsum()
daily_returns[['AAPL','strategy_returns']].plot(grid=True, figsize=(12, 8))


pf.create_simple_tear_sheet(daily_returns['strategy_returns'].diff())


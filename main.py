from hashlib import algorithms_available
import ccxt
import schedule
import pandas as pd
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import numpy as np
from datetime import datetime
import time
import math
from itertools import islice

import config
exchange = ccxt.binanceus({
    "apiKey": config.BINANCE_API_KEY,
    "secret": config.BINANCE_SECRET_KEY
})

import os
os.chdir('C:\\Users\\johnb\\Documents\\algotrading')


def last14(data):
    return data[-14:]
def last26(data):
    return data[-26:]

def window(seq, n=26):
    if not isinstance(seq, pd.DataFrame):
        return None
    it = seq.itertuples(index=False)
    result = list(islice(it, n))


    if len(result)==n:
        yield pd.DataFrame(result)
    for elem in it:
        result = result[1:] + [elem,]
        yield pd.DataFrame(result)




def RSI(data):
    # Relative Strength Index 0-100
    # rsi < 30 : oversold
    # rsi > 70 : overbought
    data = last14(data)
    changes = data.apply(lambda row: (row['close']-row['open'])/row['open'], axis=1)
    gains = []
    losses = []
    for x in changes:
        if x > 0:
            gains.append(x)
        elif x < 0:
            losses.append(x)
        else:
            gains.append(x)
            losses.append(x)
    avgGain = sum(gains)/len(gains)
    avgLoss = sum(losses)/len(losses)*-1 # make positive

    rsi = round(100 - 100/(1 + avgGain/avgLoss),2)
    return rsi


def SO(data):
    # Stochastic Oscillator 0-100
    # so < 20 : overselling
    # so > 80 : overbuying
    data = last14(data)
    C = data['close'].iloc[-1] # most recent close price
    L = min(data['low'])
    H = max(data['high'])

    so = round(100*(C-L)/(H-L),2)
    return so


def WR(data):
    # Williams %R 0-(-100)
    # "inverse" of SO
    # wr < -80 : oversold
    # so > -20 : overbought
    data = last14(data)
    C = data['close'].iloc[-1] # most recent close price
    L = min(data['low'])
    H = max(data['high'])

    wr = round(-100*(H-C)/(H-L),2)
    return wr


def ema_weight(n,k):
    b = 0.0001
    a = b/(1-math.exp(-b*n))
    weight = a*math.exp(-b*k)
    return weight

HistoricalMACD = []

def EMACD(data):
    # Exponential Moving Average Convergence Divergence
    # EMACD > 0: buy signal (oversold)
    # EMACD < 0: sell signal (overbought)
    data = list(last26(data['close']))
    p,q,r = 12, 26, 9
    EMAp, EMAq = data[-p:], data[-q:]

    for k in range(p):
        EMAp[k] = EMAp[k]*ema_weight(p, k+1)
    for k in range(q):
        EMAq[k] = EMAq[k]*ema_weight(q, k+1)

    EMAp, EMAq = sum(EMAp), sum(EMAq)

    MACD = EMAp-EMAq
    HistoricalMACD.append(MACD)

    if len(HistoricalMACD)>=9:
        EMAr = HistoricalMACD[-r:] 
        for k in range(r):
            EMAr[k] = EMAr[k]*ema_weight(r, k+1)
        EMAr = sum(EMAr)
        Signal = EMAr
        return Signal - MACD
    else: 
        return None



def OBV(data):
    # On balance volume
    # Rise in OBV: price go up
    # Drop in OBV: price go down
    pass









def first_run():
    global adaStack 
    datafile = open('datafile.txt', 'a')
    print('File opened.')
    datafile.write('timestamp\tclose\trsi\tso\twr\temacd\n')
    print(f"Running first pass at {datetime.now().isoformat()}")
    #ohlcv - [UTC, (O)pen, (H)ighest, (L)owest, (C)lose, (V)olume]
    ADAbars = exchange.fetch_ohlcv('ADA/USDT', timeframe='5m', limit=50)
    ADAdata = pd.DataFrame(ADAbars[:-1], columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    ADAdata['timestamp'] = pd.to_datetime(ADAdata['timestamp'], unit='ms')

    ADAiter = window(ADAdata)

    for point in ADAiter:
        time = point.iloc[-1]['timestamp']
        close = point.iloc[-1]['close']
        rsi = RSI(point) # calculate rsi over last 14 periods
        so = SO(point) # calculate so over last 14 periods
        wr = WR(point) # calculate wr over last 14 periods
        emacd = EMACD(point) # calculate emacd over last 12, 26, 9 periods
        datafile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(time, close, rsi, so, wr, emacd))
        adaStack = adaStack.append({'timestamp':time, 'close':close, 'rsi':rsi, 'so':so, 'wr':wr, 'emacd':emacd},ignore_index=True)
        #print(time, rsi, so, wr, emacd)
    datafile.close()
    print('File saved.')




def get_new_data():
    global adaStack

    print(f"Fetching new data for {datetime.now().isoformat()}")
    #ohlcv - [UTC, (O)pen, (H)ighest, (L)owest, (C)lose, (V)olume]
    ADAbars = exchange.fetch_ohlcv('ADA/USDT', timeframe='5m', limit=50)
    ADAdata = pd.DataFrame(ADAbars[:-1], columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    ADAdata['timestamp'] = pd.to_datetime(ADAdata['timestamp'], unit='ms')

    ADAdata = ADAdata[-26:]

    time = ADAdata.iloc[-1]['timestamp']
    if time == adaStack.iloc[-1]['timestamp']:
        pass
    else:
        datafile = open('datafile.txt', 'a')
        print('File opened.')
        close = ADAdata.iloc[-1]['close']
        rsi = RSI(ADAdata) # calculate rsi over last 14 periods
        so = SO(ADAdata) # calculate so over last 14 periods
        wr = WR(ADAdata) # calculate wr over last 14 periods
        emacd = EMACD(ADAdata) # calculate emacd over last 12, 26, 9 periods
        datafile.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(time, close, rsi, so, wr, emacd))
        adaStack = adaStack.append({'timestamp':time, 'close':close, 'rsi':rsi, 'so':so, 'wr':wr, 'emacd':emacd},ignore_index=True)
        print('New data appended to file.')
        datafile.close()
        print('File saved.')
        do_order()
        


schedule.every(10).seconds.do(get_new_data)




def do_order():
    # this will be the "algorithm"
    # determines whether or not I buy or sell based on indicators
    print('Looking to buy/sell')







class cryptoAccount:
    def __init__(self, exchange):
        self.exchange = exchange
        self.holdings = {}
        self.cash = 0
    def fetchBalance(self):
        bigDict = self.exchange.fetch_balance()
        for key in bigDict:
            if (type(bigDict[key]) is dict) and ('free' in bigDict[key]):
                val = bigDict[key]['free']
                self.holdings[key] = val
        self.cash = self.holdings['USD']
    def buy(self, crypto, percent):
        if self.exchange.has['createMarketOrder']:
            amount = percent * self.cash
            self.exchange.createMarketBuyOrder(crypto + '/USD', amount)
        else:
            pass
    def sell(self, crypto, percent):
        if self.exchange.has['createMarketOrder']:
            amount = percent * self.holdings[crypto]
            self.exchange.createMarketSellOrder(crypto + '/USD', amount)
        else:
            pass




def account_test():
    myBinance = cryptoAccount(exchange)
    myBinance.fetchBalance()
    #myBinance.buy('BTC', 0.99)
    print(myBinance.cash)
    print(myBinance.holdings)




adaStack = pd.DataFrame(columns = ['timestamp', 'close', 'rsi', 'so', 'wr', 'emacd'])
orderStack = pd.DataFrame(columns = ['timestamp', 'orderType', 'price', 'fee'])

def main():
    first_run()
    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == '__main__':
    main()
    #account_test()



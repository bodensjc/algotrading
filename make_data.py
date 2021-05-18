# built top prepare train/test data for LSTM model
# VERY similar to main.py
#
#


from hashlib import algorithms_available
import ccxt
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
os.chdir('C:\\Users\\johnb\\Documents\\algotrading\\model')

import csv




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









def make_data():
    with open('learning_data.csv', 'w', newline='') as csvfile:
        datafile = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)

        print('File opened.')
        datafile.writerow(['close', 'time', 'rsi', 'so', 'wr', 'emacd'])
        #ohlcv - [UTC, (O)pen, (H)ighest, (L)owest, (C)lose, (V)olume]
        ADAbars = exchange.fetch_ohlcv('ADA/USDT', timeframe='5m', limit=1000)
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
            if emacd is not None:
                datafile.writerow([close, time, rsi, so, wr, emacd])
            #print(time, rsi, so, wr, emacd)
        print('File saved.')





if __name__ == '__main__':
    make_data()


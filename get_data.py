import config, csv
import binance
from binance.client import Client
import os
import pandas as pd
os.chdir('C:\\Users\\johnb\\Documents\\algotrading\\model')

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY, tld='us')

candles = client.get_historical_klines("BTCUSDT",Client.KLINE_INTERVAL_5MINUTE,"1 Jan, 2020","12 Mar, 2020")

csvfile = open('5min.csv', 'w', newline='')

candlestick_writer = csv.writer(csvfile, delimiter=',')

candlestick_writer.writerow(['opentime', 'open', 'high', 'low', 'close', 'volume', 'closetime', 'qav', 'trades', 'tbbav', 'tbqav', 'ignore'])

for candlestick in candles:
    # print(candlestick)
    candlestick[0] = pd.to_datetime(candlestick[0], unit='ms')
    candlestick[6] = pd.to_datetime(candlestick[6], unit='ms')
    # dividing by 1000 puts the unix time in seconds, not milliseconds for backtrader
    candlestick_writer.writerow(candlestick)

# print(len(candles))

csvfile.close()
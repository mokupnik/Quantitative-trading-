from WrappersBinance import *
import numpy as np
import pandas as pd

class BinanceFactory():

    def __init__(self, id = np.random.randint(1, 100)):
        self.id = id

    def create_kline(self, kline, instrument):
       return Kline(kline[0],kline[6],
         pd.to_datetime(kline[0], unit='ms'),
         pd.to_datetime(kline[6], unit='ms'),
         kline[1],
         kline[4],
         kline[2],
         kline[3],
         kline[5], instrument)

    def create_kline_websocket(self, kline, instrument):
        return Kline(kline['k']['t'], kline['k']['T'],
                     pd.to_datetime(kline['k']['t'], unit='ms'),
                     pd.to_datetime(kline['k']['T'], unit='ms'),
                     kline['k']['o'],
                     kline['k']['c'],
                     kline['k']['h'],
                     kline['k']['l'],
                     kline['k']['v'],
                     instrument)

    def composeKlines(self, klines):
        n = len(klines)
        high = max(klines, key = lambda x: x.high).high
        close = klines[n-1].close
        close_dt = klines[n-1].close_dt
        close_time = klines[n-1].close_time
        open_ = klines[0].open
        open_dt = klines[0].open_dt
        open_time = klines[0].open_time
        low = min(klines, key=lambda x: x.low).low
        vol = sum(map(lambda x: float(x.vol), klines))
        instrument = klines[0].instrument
        return Kline(open_time, close_time, open_dt, close_dt, open_,
                        close, high, low, vol, instrument)











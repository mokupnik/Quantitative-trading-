import pandas as pd
import numpy as np
import binance.client
import math

from consts import BinanceConsts

class TradingAPI:
    def __init__(self,api_key, api_secret):
        self.Client = binance.client.Client(api_key, api_secret)

    def get_avg_price(self,instrument):
        return float(self.Client.get_avg_price(symbol=instrument)['price'])
    
    def get_ticker(self, instrument):
        return self.Client.get_ticker(symbol = instrument)
    
    def get_asset_balance(self, instrument = 'USDT'):
        #GET BALANCE OF GIVEN INSTRUMENT
        return self.Client.get_asset_balance(asset = instrument)
    
    def buy(self, instrument, price = None):
        
        available_funds = float(self.get_asset_balance(instrument = 'USDT')['free'])
        price = float(self.get_ticker(instrument)['askPrice'] ) + 1/2

        quantity = self.floor(available_funds / price,4)  
        
        print("Available funds {}".format(available_funds))
        print("Price {}".format(price))
        print("Quantity {}".format(quantity))
        
        order = self.Client.create_order(
            symbol=instrument,
            side=BinanceConsts.SIDE_BUY,
            type=BinanceConsts.ORDER_TYPE_LIMIT,
            timeInForce=BinanceConsts.TIME_IN_FORCE_FOK,
            quantity=quantity,
            price=str(price))
        
        return order
    
    def sell(self, instrument, price = None):
        #BTCUSDT -> BTC 
        price = float(self.get_ticker(instrument)['bidPrice'] ) - 1/2
        quantity = self.floor(float(self.get_asset_balance(instrument[:-4])['free']),4)
        
        
        order = self.Client.create_order(
            symbol=instrument,
            side=BinanceConsts.SIDE_SELL,
            type=BinanceConsts.ORDER_TYPE_LIMIT,
            timeInForce=BinanceConsts.TIME_IN_FORCE_FOK,
            quantity=quantity,
            price=str(price))
        
        return order
    
    def floor(self, x, decimal_points = 6):
        power = 10 ** decimal_points
        x *=power
        x = math.floor(x)
        x = x / power
        return x
    
    
        
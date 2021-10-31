import pandas as pd
import numpy as np
from datetime import datetime
import time
from datetime import timedelta, datetime
from TradingAPI import TradingAPI
from consts import MacioPasswords

    
class AlphaTrader:
    def __init__(self,
                currency,
                predicted_currency,
                time,
                threshold,
                database):
        self.time=time
        self.currency=currency
        self.predicted_currency=predicted_currency
        self.threshold=threshold
        self.database=database
        self.buy='sell'
        self.tradingAPI=TradingAPI(MacioPasswords.api_key, MacioPasswords.api_secret)
        self.feedback={'status': 'PENDING'}
        
    def fetch_prediction(self):
        query_params={'metric': 'model2d','from_time' : self.time, 'to_time': self.time, 'currency': self.predicted_currency ,'fields': ['scaled_forward_return']}
        query = self.database.parse_query(**query_params)
        for i in range(10):
            prediction = self.database.execute_query(query)
            if prediction.shape[0]:
                if float(prediction['_value']) > self.threshold:
                    self.buy='buy'
                elif float(prediction['_value'])> 0:
                    self.buy = 'hold'
                print('predicted return: ',float(prediction['_value']))
                break
            time.sleep(1)
        print('could not fetch predictions!')
            
    
    def attempt_transaction(self):
        for i in range(5):
            if self.buy=='buy':
                self.feedback=self.tradingAPI.buy(self.currency)
            elif self.buy=='hold':
                break
            elif self.buy=='sell':
                self.feedback=self.tradingAPI.sell(self.currency)
            if self.feedback['status'] == 'FILLED':
                print('succesful',self.feedback['side'],'with price of', self.feedback['price'])
                break
            if self.feedback['status'] =='NO ASSET':
                print('cannot', self.buy, 'because of unsifficient assets')
                break
            time.sleep(1)
        
    def save_transaction(self):
        if self.feedback['status']=='FILLED':
            kwargs={self.buy+'.v2':float(self.feedback['price'])}
            self.database.save(self.currency, 'Trader', self.time, **kwargs)
            if self.buy=='sell':
                balance=self.tradingAPI.get_asset_balance('USDT')['free']
                kwargs={'balance.v2':float(balance)}
                self.database.save(self.currency, 'Trader', self.time, **kwargs)
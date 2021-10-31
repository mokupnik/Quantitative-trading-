import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
import time
from datetime import timedelta, datetime
from TradingAPI import TradingAPI
from Trader import AlphaTrader
from consts import MacioPasswords
import httpimport
    
with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient
    
API_CLIENT = InfluxClient(
    bucket=os.environ['DB_BUCKET'],
    org=os.environ['DB_ORG'],
    token=os.environ['DB_TOKEN'],
    url=os.environ['DB_URL']
)

def parse_date(date):
    date_str = str(pd.Timestamp(date,tz='utc', unit='ms'))
    return date_str[:10]+'-'+date_str[11:16]

def run(date_str):
    startup_time = parse_date(date_str)
    
    Trader = AlphaTrader('ETHUSDT', 'BTCUSDT', startup_time, 0.04, API_CLIENT)
    Trader.fetch_prediction()
    Trader.attempt_transaction()
    Trader.save_transaction()
    
    print('attempted action: ',Trader.buy)
    print('state of transaction: ', Trader.feedback['status'])
    print('current assets in USDT:', Trader.tradingAPI.get_asset_balance('USDT')['free'])
    print('current assets in ETH: ', Trader.tradingAPI.get_asset_balance('ETH')['free'])
    
run(sys.argv[1])
    

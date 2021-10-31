import influxdb_client
import httpimport
import sys
import pandas as pd
import numpy as np
import time
import urllib3
import httpimport
import os
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from indicators.IndicatorsWriter import IndicatorsWriter
from indicators.IndicatorsCreator import IndicatorsCreator 
with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient

fields_names=['close', 'high', 'open', 'vol', 'low']
start_df = pd.DataFrame()

    
API_CLIENT = InfluxClient(
    bucket=os.environ['DB_BUCKET'],
    org=os.environ['DB_ORG'],
    token=os.environ['DB_TOKEN'],
    url=os.environ['DB_URL']
)

writer = IndicatorsWriter(API_CLIENT)
IC_eth = IndicatorsCreator(start_df)


def run(
    current_time: pd.Timestamp,
    metric: str,
    debug=False
):
    # timestamp with the right format of the newest kline in the db
    input_time = pd.Timestamp(
        datetime(
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute
        ),
        tz='utc',
        unit='ms'
    )
    try:
        data_eth = writer.on_new_data(metric, 'BTCUSDT', time = input_time, interval = 5, n = 40)
        df_eth = writer.make_df(fields_names, data_eth)

        close = df_eth['close'].copy()
        high = df_eth['high'].copy()
        df_eth['close'], df_eth['high'] = high, close

        
        fwd_returns = pd.DataFrame(high)
        
        fwd_returns['fwd_return'] = fwd_returns['high'].pct_change().shift(-1)

        fwd_returns.dropna(inplace=True)

        fwd_index = fwd_returns.last_valid_index()
        
        fwd_returns.drop(['high'], axis = 1, inplace=True)
        print("FWD RETURNS {}", fwd_returns)
        
        IC_eth.df = df_eth
        IC_eth.compute_indicators()
        
        if(len(IC_eth.features) == 0):
            raise ValueError("Missing data from last 40 klines")
        if not debug:
            print("Saving features:")
            writer.save_new_indicators(IC_eth.features, instrument = 'BTCUSDT')
            print("Saving forward return:")
            writer.save_new_indicators(fwd_returns, instrument = 'BTCUSDT')
            print("SAVED!")
        return 1
    except (
        TypeError,
        AttributeError,
        ValueError,
        urllib3.exceptions.ReadTimeoutError
    ) as e:
        print("Error:\n", e)
        return -1

    
def call_runner(date_str: str):
    try:
        startup_time = pd.Timestamp(date_str, tz='utc', unit='ms')
        startup_time += timedelta(minutes=5)
    except ValueError:
        print("Invalid date argument")
        return -1
    print("Startup time:", startup_time)
    print("indicators_runner started at {}".format(__name__, datetime.now()))  
    while (pd.Timestamp(datetime.now(), tz='utc', unit='ms') - startup_time).seconds < 240:
        result = run(
            startup_time,
            'kline5m',
        )
        if result == -1:
            print("Creating indicators failed: run returned -1. Current time {}".format(datetime.now()))
        else:
            print("Creating indicators succeeded")
            return 1
        time.sleep(0.5)
    raise Exception("Timeout")
        
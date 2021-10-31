import influxdb_client
import pandas as pd
import numpy as np
import time
import urllib3
import httpimport
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from lagged_returns import IndicatorsWriter, to_string


with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient
    
    
def init_api(
    bucket="my-bucket",
    org="ask-org",
    token="kLRh4PbhH-N7I7a0qWCkkClf1zzJFgd_u2AUZoa0_2AYXd-ow-KqAXTvi4UFyO9Dfw4vTuQRD0UZzY9S9xS4_w==",
    url="http://bogactwo.ii.uni.wroc.pl:8086"
):
    return InfluxClient(url=url,bucket=bucket, org=org, token=token)
    
    
API_CLIENT = init_api()
UTC_OFFSET = 0
INTERVAL = 1
WRITER = IndicatorsWriter(API_CLIENT)


def run(
    current_time: pd.Timestamp,
    metric: str,
    out_metric: str
):
    '''
    For a given timestamp, fetches the two newest close prices
    for BTCUSDT and ETHUSDT and calculates the lagged return
    between last two records. 
    Args:
        current_time: timestamp of the current time
        metric: passed to InfluxClient API on read
        out_metric: passed to InfluxClient API on save
    Returns:
        1 on success in saving a prediction to the database
        -1 if the function raised an exception at any point
    '''
    # Getting the timestamp of the newest lagged return record in the database 
    current_time -= timedelta(minutes=INTERVAL)
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
    print("Input time:", input_time)
    print("Datetime.now:", datetime.now())
    try:
        eth = WRITER.on_new_data(metric, 'ETHUSDT', out_metric, input_time, INTERVAL)
        btc = WRITER.on_new_data(metric, 'BTCUSDT', out_metric, input_time, INTERVAL)
        print("Lagged returns (eth, btc):", eth[3], btc[3])
        return 1
    except (
        TypeError,
        AttributeError,
        ValueError,
        urllib3.exceptions.ReadTimeoutError
    ) as e:
        print("Error:\n", e)
        raise Exception(e)


def on_new_minute():
    '''
    Waits until the kline from the last minute should be present in the db
    and calls run() function with hardcoded arguments of database arguments. 
    '''
    while True:
        current_time = pd.Timestamp(datetime.now(), tz='utc', unit='ms')
        current_time += timedelta(hours=UTC_OFFSET)
        if current_time.second == 5:
            run(
                current_time,
                'kline1m',
                out_metric='lagged_returns' + str(INTERVAL) + 'm'
            )
            break
        time.sleep(1)

        
def call_runner(): 
    print("{} started at {}".format(__name__, datetime.now()))   
    while True:  
        # Waiting for a start of a  new minute
        current_time = pd.Timestamp(datetime.now(), tz='utc', unit='ms')
        if current_time.second == 0:
            on_new_minute()
            break
        time.sleep(1)
import influxdb_client
import pandas as pd
import numpy as np
import time
import torch
import urllib3
import httpimport
from torch import nn
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from conv1d import on_new_data

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


def run(
    current_time: pd.Timestamp,
    metric: str,
    currency: str,
    field_name: str
):
    '''
    For a given timestamp, fetches the lagged returns needed
    for the 1D model and saves the model's prediction
    to the database. 
    Args:
        current_time: timestamp of the current time
        metric: passed to InfluxClient API
        currency: passed to InfluxClient API
        field_name: passed to InfluxClient API
    Returns:
        1 on success in saving a prediction to the database
        -1 if the function raised an exception at any point
    '''
    # Getting the timestamp of the newest lagged return record in the database 
    current_time -= timedelta(minutes=INTERVAL)
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
        btc_lagged_pred = on_new_data(
                metric=metric,
                currency=currency,
                field_name=field_name,
                time=input_time,
                interval=INTERVAL,
                api_client=API_CLIENT
            )
        print("History:", btc_lagged_pred[1])
        print("Predicted lagged return:", btc_lagged_pred[2])
        return 1
    except (
        TypeError,
        AttributeError,
        ValueError,
        urllib3.exceptions.ReadTimeoutError
    ) as e:
        print("Error:\n", e)
        raise Exception(e)
    
    
def call_runner():
    print("{} started at {}".format(__name__, datetime.now()))  
    current_time = pd.Timestamp(datetime.now(), tz='utc', unit='ms')
    current_time += timedelta(hours=UTC_OFFSET)
    run(
        current_time,
        metric='lagged_returns1m',
        currency='BTCUSDT',
        field_name='lagged_return'
    )

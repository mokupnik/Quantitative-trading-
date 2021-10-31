import influxdb_client
import pandas as pd
import numpy as np
import time
import urllib3
import httpimport
import json
import os
from datetime import timedelta, datetime
from indicators.Grid import Grid
from indicators.IndicatorsWriter import IndicatorsWriter
from influxdb_client.client.write_api import SYNCHRONOUS
from indicators.IndicatorsWriter import IndicatorsWriter
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
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

PATH = 'indicators/fitted.json'
writer = IndicatorsWriter(API_CLIENT)

f = open(PATH,)
jjson = json.loads(f.read())

best_features = jjson['best_features']
features_order = jjson['feature_order']
fields = jjson['fields_names']

grid = Grid(15)
grid.fit(features_order, best_features)


def run(
    current_time: pd.Timestamp,
    metric: str,
    fields_names
    
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
    print("grid_runner.run.input_time:", input_time)
    try:
        data_eth = writer.on_new_data(metric, 'BTCUSDT', time = input_time, interval = 5, n = 1.5, fields_names = fields_names)

        df_eth = writer.make_df(fields_names, data_eth)
        grid_time = df_eth.last_valid_index()
        eth_grid = grid.get_grid(df_eth)
        #print("GRID TIME {}".format(grid_time))
        #print("ETH GRID {}".format(eth_grid))
        print("BTC SHAPE {}".format(eth_grid.shape))
    
        return eth_grid, grid_time
    
    except (
        TypeError,
        AttributeError,
        ValueError,
        urllib3.exceptions.ReadTimeoutError
    ) as e:
        print("Error:\n", e)
        return None
    
    
def call_runner(date_str: str):
    try:
        startup_time = pd.Timestamp(date_str, tz='utc', unit='ms')
        startup_time += timedelta(minutes=5)
    except ValueError:
        print("Invalid date argument")
        return -1
    print("{} started at {}".format(__name__, datetime.now()))  
    if (pd.Timestamp(datetime.now(), tz='utc', unit='ms') - startup_time).seconds > 240:
        raise Exception("Timeout")
    eth_grid, grid_time = run(
        startup_time,
        'indicator',
        fields
    )
    print("GRID TIME : {}".format(grid_time))
    if eth_grid is None:
        raise Exception("Grid creator failed.")
    else:
        print("Grid created successfully.")
    return eth_grid, grid_time
          
        
if __name__ == '__main__':
    globals()[sys.argv[1]]()

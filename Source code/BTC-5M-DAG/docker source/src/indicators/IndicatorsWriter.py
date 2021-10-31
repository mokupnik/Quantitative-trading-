import influxdb_client
import pandas as pd
import numpy as np
import time
import httpimport
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS
with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


def to_string(date_time):
    
    return date_time.strftime("%Y-%m-%d-%H:%M")


class IndicatorsWriter:
    
    def __init__(
        self,
        api_client
    ):
        self.api_client = api_client
        
    
    def get_time_range(self, time, interval, n):
        return time - timedelta(minutes = n*interval), time
    
    def make_query(self, metric, currency, start_time, end_time, fields):
        query_params={
             'metric': metric,
             'currency': currency,
             'from_time': to_string(start_time),
             'to_time': to_string(end_time),
             'fields': fields
         }
        return query_params
        
    def on_new_data(self,
        metric,
        currency,
        time: pd.Timestamp,
        interval: int,
        fields_names=['close', 'high', 'open', 'vol', 'low'],
        n = 20
    ):
        start_time, end_time = self.get_time_range(time, interval, n)
        print("Start time, end time for fetching 5m klines:", start_time, end_time)
        query_params = self.make_query(metric, currency, start_time, end_time, fields_names)
        query = self.api_client.parse_query(**query_params) 
        fetched_data = self.api_client.execute_query(query)
        return fetched_data
    
    def make_df(self, fields_names, df):

        new_df = pd.DataFrame()

        index = df[df._field == fields_names[0]]["_time"]
        
        new_df["time"] = index

        new_df.set_index(['time'], inplace = True)
        for idx,x in enumerate(fields_names):
            values = df[df._field == x]._value.to_numpy()
            new_df[x] =  values

        return new_df

    def save_new_indicators(self, df, instrument):

        len_index = len(df) -1
        new_indicators_time = df.last_valid_index()
        new_indicators_values = df.iloc[len_index]
        print("New_indicators_time {}".format(new_indicators_time))

        time = pd.to_datetime(new_indicators_time, unit = 'ms') 

        params = {}
        for x in df.columns:
            params[x] = float(df.iloc[len_index][x])
        

        self.api_client.save(instrument, 'indicator', time, **params)

        

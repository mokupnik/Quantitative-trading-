import httpimport
import influxdb_client
import pandas as pd
import numpy as np
import time
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS


with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient

with httpimport.github_repo(
    "DZAlpha", "utility", module='functions'
):
    from functions import to_string   


class IndicatorsWriter:
    '''
    Uses InfluxClient to calculate and save lagged returns.
    '''
    def __init__(
        self, 
        api_client
    ):
        self.api_client = api_client
        
    def get_lagged_return(self, x_old, x_new):
        return x_new / x_old - 1
      
    def get_time_range(self, time, interval):
        '''
        Returns a tuple of two pd.Timestamps (start, end)
        which denote the time range to feed to Influx.
        Args:
            time: pd.Timestamp when the new record was introduced
            interval: interval of the observations in minutes
        '''
        return time - timedelta(minutes=interval), time   
      
    def save_to_db(self, time, metric, currency, value):
        self.api_client.save(
            currency, 
            metric, 
            time=time, 
            lagged_return=value
        )
        
    def on_new_data(
        self,
        metric,
        currency,
        out_metric,
        time: pd.Timestamp,
        interval: int,
        field_name='close',
    ):
        '''
        Fetches two close prices from the database 
        and calculates the lagged return between them. 
        Saves the lagged return in a field called lagged_return.
        Args:
            metric: metric used to fetch the data
            currency: currency used to fetch the data
            out_metric: metric used to save the lagged return
            time: datetime object of the newest close price in the db.
                datetime of the second close price will be determined
                as 'time' subtracted by the 'interval' argument.
                It has to be a pd.Timestamp with the timezone set to 'utc'
            interval: interval of the observations in minutes,
                e.g. 5 for 5 minute klines
            field_name: field name of the close price 
        '''
        # Start_time for the influx range has to include the datetime of the previous record
        start_time, end_time = self.get_time_range(time, interval)
        query_params={
            'metric': metric,
            'currency': currency,
            'from_time': to_string(start_time),
            'to_time': to_string(end_time),
            'fields': [field_name]
        }
        query = self.api_client.parse_query(**query_params)
        fetched_data = self.api_client.execute_query(query)
        # Retrieving the newest record and the second-newest one
        prev_record = float(
            fetched_data[fetched_data._time==start_time]._value
        )
        curr_record = float(
            fetched_data[fetched_data._time==end_time]._value
        )
        lagged_return = self.get_lagged_return(prev_record, curr_record)
        print("Saving at {}".format(end_time))
        self.save_to_db(
            end_time,
            out_metric,
            currency,
            lagged_return
        )
        return fetched_data, prev_record, curr_record, lagged_return
        
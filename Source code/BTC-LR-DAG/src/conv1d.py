import influxdb_client
import pandas as pd
import numpy as np
import time
import torch
import httpimport
from torch import nn
from datetime import timedelta, datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from model import Model 


with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient

    
with httpimport.github_repo(
    "DZAlpha", "utility", module='functions'
):    
    from functions import to_string, get_time_range 
    
class Conv1D(nn.Module):
    def __init__(self,
                 in_size, 
                 out_channels=32, 
                 kernel_size=5, 
                 pool_size=2,
                 maxpool_padding=0,
                 loss_fun=torch.nn.MSELoss(),
                 dtype=torch.float64):
        super(Conv1D, self).__init__()
        
        self.conv_out = int((in_size - kernel_size + 1 + maxpool_padding) * out_channels / pool_size)
        self.conv = nn.Sequential(
            nn.Conv1d(
                in_channels=1,
                out_channels=out_channels,
                kernel_size=kernel_size),
            nn.ReLU(),
            nn.MaxPool1d(pool_size, padding=maxpool_padding),
            nn.Flatten()
            )
    
        self.linear = nn.Sequential(
            nn.Linear(self.conv_out, 1)
            )
        self.loss_fun = loss_fun
        self.to(dtype=dtype)

    def forward(self, X):
        X = self.conv(X)
        X = self.linear(X)
        return X

    def loss(self, out, targets):
        return self.loss_fun(out, targets)


def extract_data(
    fetched_data,
    input_size,
    end_time
):
    '''
    Extracts the lagged returns from dataframe
    fetched from the database. 
    If any record that should be there is missing,
    ValueError is raised. 
    Args:
        fetched_data: dataframe fetched from influx
        input_size: number of lagged returns to extract
        end_time: time of the last lagged return in the 
            fetched_data
    '''
    lagged_returns = []
    fetched_data_dates = list(fetched_data['_time'])
    for i in range(input_size):
        record_time = end_time - timedelta(minutes=i)
        if record_time not in fetched_data_dates:
            #print(record_time, "not present in fetched data")
            raise ValueError("{} not present in fetched data".format(record_time))
        else:
            newest_record = float(
                fetched_data[fetched_data._time==record_time]._value
            )
            lagged_returns.append(newest_record)
    lagged_returns = torch.tensor(
        lagged_returns,
        dtype=torch.float64
    ) * 100
    return lagged_returns.reshape(1, 1, len(lagged_returns))
    


def on_new_data(
    metric: str,
    currency: str,
    field_name: str,
    time: pd.Timestamp,
    interval: int,
    api_client: InfluxClient,
    input_size=20
):
    '''
    Fetches data for the 1D Model, runs the model 
    to obtain the prediction and saves it to the database. 
    Args:
        metric: metric passed to InfluxClient query
        currency: currency passed to InfluxClient query
        field_name: field name passed to InfluxClient query
        time: datetime object of a new value in database
            It has to be a pd.Timestamp with timezone set to 'utc'
        interval: interval of the observations in minutes,
            e.g. 5 for 5 minute klines
        api_client: client used to communicate with the database
        input_size: number of lagged returns that form an input for the model
    '''
    model1d = Model("config/btc_model1d.pth", Conv1D(in_size=input_size))
    start_time, end_time = get_time_range(time, interval * input_size)
    
    query_params={
        'metric': metric,
        'currency': currency,
        'from_time': to_string(start_time),
        'to_time': to_string(end_time),
        'fields': [field_name]
    }
    query = api_client.parse_query(**query_params)
    
    fetched_data = api_client.execute_query(query)
    try:
        lagged_returns = extract_data(
            fetched_data,
            input_size,
            end_time
        ).to(model1d.device)
    except ValueError as e:
        print(e)
        return fetched_data, None, None
        
    prediction_time = end_time + timedelta(minutes=interval)    
    with torch.no_grad():
        predicted_lagged_return = model1d.model.forward(lagged_returns)
        
    api_client.save(
        currency=currency,
        metric='model1d',
        time=prediction_time, 
        lagged_return=float(predicted_lagged_return)
    )
    return fetched_data, lagged_returns, predicted_lagged_return
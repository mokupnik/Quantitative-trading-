import torch
import httpimport
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from models.conv2d import Conv2D
from models.predictor import Predictor
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

MODEL_DIR = "indicators/config/eth100k_08-01-01_1channel.pth"
SCALER_DIR = "indicators/config/scaler.save"
UTC_OFFSET = 0
CONV_2D = Conv2D(15, 15, conv_out=800)


def run(grid, grid_time):
    '''
    Creates a Predictor instance and runs predict_and_save
    with provided input.
    Parameters
    --------
    grid: torch.tensor with a single input for the Conv2D model
    grid_time: pd.Timestamp containing timestamp from when the grid
        comes from
    '''
    predictor = Predictor(MODEL_DIR, CONV_2D, SCALER_DIR)
    save_time = grid_time + timedelta(minutes=0)
    print("Grid has been created for the kline at {}".format(grid_time))
    print("Saving the prediction at {}".format(save_time))
    predictor.predict_and_save(grid, save_time, API_CLIENT, out_metric='model2d')
    

def call_runner(grid, grid_time):
    '''
    Function used by the main runner to envoke the predictor workflow. 
    Parameters
    --------
    grid: torch.tensor with a single input for the Conv2D model
    grid_time: pd.Timestamp containing timestamp from when the grid
        comes from
    '''
    print("{} started at {}".format(__name__, datetime.now()))   
    run(grid, grid_time)
    
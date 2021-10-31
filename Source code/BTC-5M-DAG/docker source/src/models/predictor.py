import httpimport
import joblib
import pandas as pd
import torch
import numpy as np
from sklearn.preprocessing import MinMaxScaler
with httpimport.github_repo(
    "DZAlpha", "utility", module='model'
):
    from model import Model
with httpimport.github_repo(
    "DZAlpha", "utility", module='influx'
):
    from influx import InfluxClient
    
    
class Predictor(Model):
    def __init__(
        self, 
        model_dir, 
        model_obj,
        scaler_dir
    ):
        super().__init__(model_dir, model_obj)
        self.scaler = joblib.load(scaler_dir) 
        self.scaler.clip = False
        
    def reshape_for_scaling(self, X):
        return X.reshape((X.shape[0], X.shape[1] * X.shape[2]))

    def restore_og_shape(self, X, fst_axis, snd_axis):
        return X.reshape((X.shape[0], fst_axis, snd_axis))
    
    def preprocess_grid(self, grid):
        scaled_grid = self.scaler.transform(
            self.reshape_for_scaling(grid)
        )
        return torch.tensor(
            np.expand_dims(self.restore_og_shape(scaled_grid, 15, 15), 1),
            dtype=torch.float64
        ).to(self.device)
    
    def do_prediction(self, grid):
        processed_grid = self.preprocess_grid(grid)
        with torch.no_grad():
            prediction = self.model.forward(processed_grid)
            return prediction
        
    def predict_and_save(
        self, 
        grid, 
        save_time: pd.Timestamp,
        api_client,
        out_metric: str
    ):
        '''
        Parameters
        ----------
        grid: ndarray or torch.tensor with grid of indicators
        save_time: Used as a time to which a prediction 
            will be saved in the database.
        api_client: InfluxClient API instance 
        out_metric: metric name passed to InfluxClient API
        '''
        prediction = self.do_prediction(grid)
        print("Prediction: {}".format(prediction))
        api_client.save(
            currency='BTCUSDT',
            metric=out_metric,
            time=save_time, 
            scaled_forward_return=float(prediction)
        )
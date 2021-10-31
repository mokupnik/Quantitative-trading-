import talib as ta
import pandas as pd
import numpy as np 
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
from tqdm import tqdm

class IndicatorsCreator:
    def __init__(self, 
                 df, 
                 T = list(range(6,21)), 
                 dim=15,
                 ):
        self.df = df
        self.T = T
        self.mi = {}
        self.mutual_info_df = pd.DataFrame()
        self.best_features = []
        self.mi_by_indicator = pd.DataFrame()
        self.dim = dim
        self.features = pd.DataFrame()
        self.features_order = []
        self.targets = pd.DataFrame()
        
    def compute_indicators(self):
        for t in self.T:
            self.df[f'{t}_SMA'] = ta.SMA(self.df.close,timeperiod =t)
            self.df[f'{t}_EMA'] = ta.EMA(self.df['close'].values,t)
            self.df[f'{t}_WMA'] = ta.WMA(self.df['close'].values,t)
            self.df[f'{t}_RSI'] = ta.RSI(self.df['close'],t)
            self.df[f'{t}_WILLR'] = ta.WILLR(self.df.high, self.df.low, self.df.close, t)
            self.df[f'{t}_NATR'] = ta.NATR(self.df.high, self.df.low, self.df.close,t)
            self.df[f'{t}_CCI'] = ta.CCI(self.df.high, self.df.low, self.df.close,t)
            self.df[f'{t}_CMO'] = ta.CMO(np.asarray(self.df['close']), t)
            self.df[f'{t}_ROC'] = ta.ROC(self.df['close'],t)
            self.df[f'{t}_MOM'] = ta.MOM(self.df['close'],t)
            self.df[f'{t}_HIGHBB'], self.df[f'{t}_MIDBB'], self.df[f'{t}_LOWBB'] = ta.BBANDS(self.df.close, timeperiod= t, matype=0)
            self.df[f'{t}_ADOSC'] = ta.ADOSC(self.df.high, self.df.low, self.df.close,self.df.vol, fastperiod=t-3, slowperiod=t+4)
            self.df[f'{t}_ADX'] = ta.ADX(self.df.high, self.df.low, self.df.close, t)
            self.df[f'{t}_PPO'] = ta.PPO(self.df.close, fastperiod =t, matype = 1)
            self.df[f'{t}_APO'] = ta.APO(self.df.close, fastperiod=t, slowperiod = t+4, matype=0)
            self.df[f'{t}_KAMA'] = ta.KAMA(self.df.close,t)
            self.df[f'{t}_ATR'] = ta.ATR(self.df.high, self.df.low, self.df.close, t)
            self.df[f'{t}_DX'] = ta.DX(self.df.high, self.df.low, self.df.close, t)
            _, _,self.df[f'{t}_MACDHIST'] = ta.MACD(self.df.close)
            self.df[f'{t}_MFI'] = ta.MFI(self.df.high, self.df.low, self.df.close, self.df.vol, t)
        self.df = self.df.dropna()
        self.features = self.df.copy()
        self.features = self.features.drop(["close", "high", "vol", "low", "open"], axis=1)

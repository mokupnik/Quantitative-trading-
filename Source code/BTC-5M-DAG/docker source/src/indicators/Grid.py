import json
import pandas as pd
import numpy as np

class Grid:
    def __init__(self, size = 15):
        self.size = size
        
    def fit(self, feature_order, best_features):
        self.feature_order = feature_order
        self.best_features = best_features

    def cluster(self):
        new_cols = {}
        for feature in self.best_features:
            fnames = sorted(self.features.filter(like=f'_{feature}').columns.tolist())
            renamed = [f'{i:02}_{feature}' for i in range(1, len(fnames)+ 1)]
            new_cols.update(dict(zip(fnames, renamed)))
        self.features = self.features.rename(columns=new_cols).sort_index(1)

    def get_grid(self, df):
        self.features = df
        self.cluster()
        self.features = self.features.loc[:, self.feature_order]
        self.features = self.features.apply(pd.to_numeric, downcast='float')
        return self.features.to_numpy().reshape(-1,self.size, self.size)
    
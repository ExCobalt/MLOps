import numpy as np
import pandas as pd

from models.CoxModel import CoxModelFitter
from lifelines import KaplanMeierFitter
from statsmodels.discrete.discrete_model import Logit


MODEL_TYPES = [
    {'id': 1, 'name': 'Logit'},
    {'id': 2, 'name': 'Kaplan-Meier'},
    {'id': 3, 'name': 'Cox'},
]


class Model(object):
    
    def __init__(self) -> None:
        self.set_model_type(1)
        self.get_data()
    
    
    def get_data(self):
        
        data = pd.read_csv('support/survival_test_data.csv', sep=';', decimal=',')
        
        data['dtAgrmntOpen'] = pd.to_datetime(data['dtAgrmntOpen']) + pd.offsets.MonthEnd(0)
        data['dtAgrmntClose'] = pd.to_datetime(data['dtAgrmntClose']) + pd.offsets.MonthEnd(0)
        
        data['dtReport'] = (
            data['dtAgrmntOpen'].values.astype('datetime64[M]').astype(np.int64)
            + data['nMonth'] - 1
            ).astype('datetime64[M]') + pd.offsets.MonthEnd(0)
        
        data['dmIsExpired'] = (data['dtReport'] >= data['dtAgrmntClose']).astype(np.int8)
        
        self.data = data
        return f'Loaded survival data sample'
    
    
    def set_model_type(self, type_id):
        self.model_type = type_id
        return f'Model type changed to {MODEL_TYPES[type_id]}'
    
    
    def fit(self):
        if self.model_type == 'Logit':
            pass
        elif self.model_type == 'Kaplan-Meier':
            pass
        elif self.model_type == 'Cox':
            pass
        else:
            return None

    
    def predict(self, data=None):
        if data is None:
            data = self.data
        pass
    
    def save(self, slot):
        pass
    
    def restore(self, slot):
        pass
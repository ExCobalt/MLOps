import pickle
import numpy as np
import pandas as pd
from datetime import datetime

import statsmodels.api as sm
from lifelines import KaplanMeierFitter
from models.CoxModel import CoxModelFitter


MODEL_TYPES = [
    {'id': 1, 'name': 'Logit'},
    {'id': 2, 'name': 'Kaplan-Meier'},
    {'id': 3, 'name': 'Cox'},
]

MODELS_DICT = {
    model_type['id']: model_type['name']
    for model_type in MODEL_TYPES
    }

SAVE_DIR = './tmp'


class Model(object):
    
    def __init__(self) -> None:
        self.set_model_type(1)
        self.get_data()
    
    
    def get_data(self):
        
        data = pd.read_csv('./support/survival_test_data.csv', sep=';', decimal=',')
        
        data['dtAgrmntOpen'] = pd.to_datetime(data['dtAgrmntOpen']) + pd.offsets.MonthEnd(0)
        data['dtAgrmntClose'] = pd.to_datetime(data['dtAgrmntClose']) + pd.offsets.MonthEnd(0)
        
        data['dtReport'] = (
            data['dtAgrmntOpen'].values.astype('datetime64[M]').astype(np.int64)
            + data['nMonth'] - 1
            ).astype('datetime64[M]') + pd.offsets.MonthEnd(0)
        
        data['dmIsExpired'] = (data['dtReport'] >= data['dtAgrmntClose']).astype(np.int8)
        
        self.data = data
        return f'Loaded survival data sample'
    
    
    def set_model_type(self, type_id: int):
        if type_id not in MODELS_DICT.keys():
            raise KeyError(f'Model type with id {type_id} does not exist')
        self.model_type = MODELS_DICT[type_id]
        return f'Model type changed to {MODELS_DICT[type_id]}'
    
    
    def fit_logit(self, specification: list = None, fit_intercept: bool = True):
        if not fit_intercept and specification is None:
            raise ValueError('''Empty specification without intercept 
                                allowed only for Kaplan-Meier estimator''')
        if fit_intercept:
            if specification is None:
                specification = ['intercept']
                X = np.ones(self.data.shape[0])
            else:
                specification = specification + ['intercept']
        
        X = self.data[specification]
        if fit_intercept:
            X = sm.add_constant(X)
        model = sm.Logit(self.data['dmIsExpired'], X)
        return model
    
    
    def fit(self, specification: list = None, fit_intercept: bool = True):
        
        if self.model_type == 'Logit':
            self.model = self.fit_logit(specification, fit_intercept)
            
        elif self.model_type == 'Kaplan-Meier':
            if fit_intercept:
                return 'Intercept will not be used. Kaplan-Meier is non-parametric estimator'
        
        elif self.model_type == 'Cox':
            if fit_intercept:
                return 'Cox regression does not allow intercept'
            if specification is None:
                return 'Cox regression with empty specification fails to Kaplan-Meier estimator'
        
        else:
            return None
        
        self.model_uid = datetime.now().strftime('%y%m%d_%H%M%S')
        return 'Successfuly fitted'
    
    
    def summary(self):
        summary = self.model.summary()
        if self.model_type == 'Logit':
            pass
        elif self.model_type == 'Kaplan-Meier':
            pass
        elif self.model_type == 'Cox':
            pass
        return summary
    
    
    def predict(self, data=None):
        if data is None:
            data = self.data
        try:
            result = self.model.predict(data)
            return result
        except Exception as e:
            return e

 
    def save(self, path=None):
        if path is None:
            path = f'{SAVE_DIR}/{self.model_type}/{self.model_uid}'
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        return f'Saved model to {path}'
    
    
    def restore(self, path=None, model_uid=None):
        if path is not None:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
        elif model_uid is not None:
            path = f'{SAVE_DIR}/{self.model_type}/{model_uid}'
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            return 'Path or model uid not provided'
        return f'Load model from {path}'

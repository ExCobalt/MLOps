import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine

import statsmodels.api as sm
from lifelines import KaplanMeierFitter
from models.cox_fitter import CoxModelFitter


MODEL_TYPES = [
    {'name': 'Logit', 'type': 'parametric'},
    {'name': 'Kaplan-Meier', 'type': 'nonparametric'},
    {'name': 'Cox', 'type': 'semiparametric'},
]

MODELS_LIST = [model_type['name'] for model_type in MODEL_TYPES]

CHECKPOINT_DIR = './.tmp'


class Model(object):
    
    def __init__(self) -> None:
        self.models_list = MODELS_LIST
        self.clear_model()
        self.set_model_type('Logit')
        self.sql_conn = create_engine('postgresql://postgres:v45wbge8rl@localhost:5432/postgres')
        self.get_data(table='survival')
    
    
    def clear_model(self):
        self.model = None
    
    
    def get_data(self, table=None):
        self.data = pd.read_sql(table, con=self.sql_conn)
    
    
    def set_model_type(self, model_name: str):
        if model_name not in MODELS_LIST:
            raise KeyError(f'Model type with id {model_name} does not exist')
        if hasattr(self, 'model_type'):
            if self.model_type != model_name:
                self.clear_model()
        self.model_type = model_name
        return True
    
    
    def fit_logit(self, specification: list = None, fit_intercept: bool = False):
        if specification is None:
            if fit_intercept:
                specification = ['intercept']
                X = np.ones(self.data.shape[0])
        else:
            X = self.data[specification]
            if fit_intercept:
                specification = specification + ['intercept']
                X['intercept'] = np.ones(X.shape[0])
        self.clear_model()
        fitted = sm.Logit(self.data['dmIsExpired'], X).fit(disp=False)
        return fitted
    
    
    def fit_km(self):
        self.clear_model()
        fitted = KaplanMeierFitter().fit(self.data['nMonth'], self.data['dmIsExpired'])
        return fitted
    
    
    def fit_cox(self, id_col: str = 'nAgrmntId', start_col: str = None, stop_col: str = 'nMonth', 
                event_col: str = 'dmIsExpired', specification: list = None):
        X = self.data
        if start_col is None:
            start_col = 'start_col'
            X[start_col] = X[stop_col] - 1
        
        varlist = specification + [id_col, start_col, stop_col, event_col]
        X = X[varlist]
        self.clear_model()
        fitted = CoxModelFitter().fit(X, id_col=id_col, event_col=event_col, 
                                      start_col=start_col, stop_col=stop_col)
        return fitted
    
    
    def fit(self, specification: list = None, fit_intercept: bool = False, **kwargs):
        
        if self.model_type == 'Logit':
            if not fit_intercept and specification is None:
                raise ValueError('''Empty specification without intercept 
                                 allowed only for Kaplan-Meier estimator''')
            self.model = self.fit_logit(specification, fit_intercept)
        
        elif self.model_type == 'Kaplan-Meier':
            if fit_intercept:
                return 'Intercept cannot be set. Kaplan-Meier is non-parametric estimator'
            if specification is not None:
                return 'Specification cannot be set. Kaplan-Meier is non-parametric estimator'
            self.model = self.fit_km()
        
        elif self.model_type == 'Cox':
            if fit_intercept:
                return 'Cox regression does not allow intercept'
            if specification is None:
                return 'Cox regression with empty specification fails to Kaplan-Meier estimator'
            self.model = self.fit_cox(specification=specification, **kwargs)
        
        else:
            return None
        
        self.model_uid = datetime.now().strftime('%y%m%d_%H%M%S')
        return True
    
    
    def summary(self):
        if self.model_type == 'Logit':
            return self.model.summary()
        elif self.model_type == 'Kaplan-Meier':
            return self.model.survival_function_
        elif self.model_type == 'Cox':
            return self.model.print_summary()
        return summary
    
    
    def predict(self, data=None):
        if data is None:
            data = self.data
        try:
            result = self.model.predict(data)
            return result
        except Exception as e:
            return e
        
    def list_all_fitted(self):
        path = Path(f'{CHECKPOINT_DIR}/{self.model_type}/').glob('**/*')
        files = [x for x in path if x.is_file()]
        return files

 
    def save(self, path=None):
        if path is None:
            path = f'{CHECKPOINT_DIR}/{self.model_type}/{self.model_uid}'
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        return f'Saved model to {path}'
    
    
    def restore(self, path=None, model_uid=None):
        if path is not None:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
        elif model_uid is not None:
            path = f'{CHECKPOINT_DIR}/{self.model_type}/{model_uid}'
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            return 'Path or model uid not provided'
        return f'Load model from {path}'

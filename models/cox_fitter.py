import scipy
import numpy as np
import pandas as pd

from lifelines import CoxTimeVaryingFitter


def VarianceThresholdSelector(X):
    atol = 1e-4
    rtol = 1e-4
    tol = atol + rtol * X.var(0)
    r = np.linalg.qr(X, mode='r')
    mask = np.abs(r.diagonal()) < np.sqrt(tol)
    return mask


def VarianceThresholdSelectorCox(X, threshold=2e-4):
    return X.var(0) < threshold


class CoxModelFitter(CoxTimeVaryingFitter):
    
    def __init__(self, alpha=0.05, penalizer=0.0, l1_ratio=0.0, strata=None):
        super().__init__(alpha=alpha, penalizer=penalizer, l1_ratio=l1_ratio, strata=strata)

    
    def _compute_baseline_survival_custom(self, df):
        
        df = df.copy()
        
        if self.weights_col is None:
            assert "__weights" not in df.columns, "__weights is an internal lifelines column, please rename your column first."
            df["__weights"] = 1.0
        
        df = df.rename(columns={self.event_col: "event", self.start_col: "start", 
                                self.stop_col: "stop", self.weights_col: "__weights"})
        
        events, start, stop = (
            df.pop("event").astype(bool),
            df.pop("start"),
            df.pop("stop"),
            )
        weights = df.pop("__weights").astype(np.float32)
        
        unique_death_times = np.unique(stop[events.values])
        baseline_survival = pd.DataFrame(np.zeros_like(unique_death_times), 
                                         index=unique_death_times, 
                                         columns=['S0_diff'])
        
        hazards = np.exp(df[self.params_.index].values @ self.params_.values)
        
        np.seterr(over='ignore')
        for t in unique_death_times:
            id_at_risk = (t > start.values) & (t <= stop.values)
            
            events_at_t = events.values[id_at_risk]
            weights_at_t = weights.values[id_at_risk]
            events_at_t_sum = (weights_at_t.squeeze() * events_at_t).sum()
            
            hazards_at_t = hazards[id_at_risk]
            hazards_at_t_sum = np.sum(hazards_at_t)
            hazards_at_event_at_t = hazards_at_t[events_at_t]
            
            # начальное значение
            init_val = np.exp(- events_at_t_sum / hazards_at_t_sum)
            
            """ 
            # Проблемы со сходимостью, возможно ошибка. Проверить формулу
            stops_at_t = stop.values[id_at_risk]
            deaths_at_t = events.values[id_at_risk] & (stops_at_t == t)
            deaths_at_t_sum = (weights_at_t.squeeze() * deaths_at_t).sum()
            init_val = np.exp(- deaths_at_t_sum / hazards_at_t_sum) 
            """
            
            # базовая выживаемость - решение данного уравнения по 'с' [где g(x)=exp(Xb)] :
            # sum[по выбывшим](g(x) / (1 - c^g(x))) = sum[по всем](g(x))
            f = lambda c: (
                np.sum(hazards_at_event_at_t / (1 - c**hazards_at_event_at_t)) - hazards_at_t_sum
                ) ** 2
            baseline_survival.loc[t] = scipy.optimize.minimize(f, init_val, method='l-bfgs-b', bounds=[(1e-8,1-1e-8)]).x
        
        np.seterr(over='warn')
        
        # Заполняем пропущенные периоды
        baseline_survival = baseline_survival.merge(
            pd.DataFrame(index = range(1, max(stop)+1)),
            how='outer', left_index=True, right_index=True
            ).fillna(1)
        
        return baseline_survival

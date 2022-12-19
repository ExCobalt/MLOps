import numpy as np
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:password@dev:5432/postgres')

data = pd.read_csv('./support/survival_test_data.csv', sep=';', decimal=',')

data['dtAgrmntOpen'] = pd.to_datetime(data['dtAgrmntOpen']) + pd.offsets.MonthEnd(0)
data['dtAgrmntClose'] = pd.to_datetime(data['dtAgrmntClose']) + pd.offsets.MonthEnd(0)

data['dtReport'] = (
    data['dtAgrmntOpen'].values.astype('datetime64[M]').astype(np.int64)
    + data['nMonth'] - 1
    ).astype('datetime64[M]') + pd.offsets.MonthEnd(0)

data['dmIsExpired'] = (data['dtReport'] >= data['dtAgrmntClose']).astype(np.int8)

for i in ['ctgrCardLevel', 'ctgrSalesChannel', 'dmMassOffer', 'nIsPayroll']:
    data[i] = data[i].astype(np.int8)

data.to_sql('survival', con=engine, if_exists='replace')

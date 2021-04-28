
import pandas as pd
import numpy as np
#from multiprocessing import cpu_count
#from warnings import catch_warnings
#from warnings import filterwarnings
from pmdarima.arima import auto_arima
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')

df = pd.read_sql_table('orderproducts_top20', engine)
prod_monthly = pd.crosstab(df['order_date'], df['product_sku']).resample('M').sum()
prod_monthly = prod_monthly['2018-01':'2021-03']
items = prod_monthly.columns

# Select the best model using auto_arima using one of the dataset
temp = prod_monthly['2018':'2020']['EFX-FLY-BLK'].values

stepwise_model = auto_arima(temp, start_p=1, start_q=1,
                           max_p=3, max_q=3,
                           start_P=0, start_Q=0,
                           d=1, D=1,
                           seasonal=True, m=12,
                           trace=True,
                           error_action='ignore',
                           suppress_warnings=True,
                           stepwise=True)

# Forecast the last 3 month sales for the top 20 items
# items are the names of the top20 items
test_predict = []
results = pd.DataFrame()
trend = 'c'

for item in items:
    mse_list = []
    params = []
    data = prod_monthly[item]
    train = data.iloc[:-3]
    test = data.iloc[-3:]

    # the order and sorder is derived above
    order, sorder = stepwise_model.order, stepwise_model.seasonal_order

    model = SARIMAX(train, order=order, seasonal_order=sorder,
                            trend=trend, enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit(disp=False)
    forecast = model_fit.predict(len(train), len(train)+3)
    adj_forecast = [0 if x < 0 else int(round(x)) for x in forecast]
    item_name = [item for x in range(3)]
    params.append([order, sorder, trend])
    rmse = round(np.sqrt(mean_squared_error(test, adj_forecast[0:3])), 2)
    diff = abs(sum(test.values - adj_forecast[0:3]))
    res = pd.DataFrame(zip(item_name, np.array(test), np.array(adj_forecast)),
                       index=['m+1', 'm+2', 'm+3'], columns=['item', 'test', 'predict'])
    res['rmse'] = ''
    res.loc['m+1', 'rmse'] = rmse
    res['abs(diff)'] = ''
    res.loc['m+1', 'abs(diff)'] = diff
    results = pd.concat([results, res], axis=0)

# #### Writing to database
results = results.reset_index().rename(columns={'index': 'month'})
results.to_sql(name='top20forecasts_SARIMA', con=engine, if_exists='replace', index=False)
# results.to_csv('../data-processed/top20forecasts_SARIMA_01to03.csv')

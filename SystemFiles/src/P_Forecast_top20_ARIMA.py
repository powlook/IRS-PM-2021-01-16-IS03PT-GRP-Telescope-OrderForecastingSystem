# Forecasting top20 items from orderproducts

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine
from pmdarima.arima import auto_arima

engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')

df = pd.read_sql_table('orderproducts_top20', engine)
prod_monthly = pd.crosstab(df['order_date'], df['product_sku']).resample('M').sum()
prod_monthly = prod_monthly['2018-01':'2021-03']
items = prod_monthly.columns

# items are the names of the top20 items
results = pd.DataFrame()
for item in items:
    data = prod_monthly[item]
    train = data.iloc[:-3]
    test = data.iloc[-3:]

    # Select the best model using auto_arima
    stepwise_model = auto_arima(train, start_p=1, start_q=1,
                               max_p=2, max_q=2, m=12,
                               start_P=0, seasonal=True,
                               d=1, D=1, trace=False,
                               error_action='ignore',
                               suppress_warnings=True,
                               stepwise=True)
    stepwise_model.fit(train)

    forecast = stepwise_model.predict(n_periods=3)
    adj_forecast = [0 if x < 0 else int(round(x)) for x in forecast]
    item_name = [item for x in range(3)]
    rmse = round(np.sqrt(mean_squared_error(test, adj_forecast)), 2)
    res = pd.DataFrame(zip(item_name, np.array(test), np.array(adj_forecast)),
                       index=['m+1', 'm+2', 'm+3'], columns=['item', 'test', 'predict'])
    res['rmse'] = ''
    res.loc['m+1', 'rmse'] = rmse
    results = pd.concat([results, res], axis=0)


# Write to database
results = results.reset_index().rename(columns={'index': 'month'})
results.to_sql(name='top20forecasts_ARIMA', con=engine, if_exists='replace', index=False)

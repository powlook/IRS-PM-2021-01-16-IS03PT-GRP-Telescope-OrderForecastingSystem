
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')

df = pd.read_sql_table('orderproducts_top20', engine)
prod_monthly = pd.crosstab(df['order_date'], df['product_sku']).resample('M').sum()
prod_monthly = prod_monthly['2018-01':'2021-03']
items = prod_monthly.columns

# Forecast the last 3 month sales for the top 20 items
# items are the names of the top20 items

test_predict = []
mse_list = []
results = pd.DataFrame()

for item in items:
    data = prod_monthly[item]
    train = np.array(data.iloc[:-3])
    test = np.array(data.iloc[-3:])
    mth_yr = data.index
    forecast = np.empty(3)
    forecast.fill(int(np.array(train[-3:]).mean()))
    adj_forecast = [0 if x < 0 else int(round(x)) for x in list(forecast)]
    item_name = [item for x in range(3)]
    rmse = round(np.sqrt(mean_squared_error(test, adj_forecast[:3])), 2)
    diff = abs(sum(test - adj_forecast[:3]))
    res = pd.DataFrame(zip(item_name, test, adj_forecast),
                       index=['m+1', 'm+2', 'm+3'], columns=['item', 'test', 'forecast'])
    res['rmse'] = ''
    res.loc['m+1', 'rmse'] = float(rmse)
    res['abs(diff)'] = ''
    res.loc['m+1', 'abs(diff)'] = diff
    results = pd.concat([results, res], axis=0)

results = results.reset_index().rename(columns={'index': 'month'})
results.to_sql(name='top20forecasts_MA', con=engine, if_exists='replace', index=False)
# results.to_csv('../data-processed/top20forecasts_RollingMA_01to03.csv')

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.api import ExponentialSmoothing

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')

# load dataset from DB
df = pd.read_sql_table('orderproducts_top20', engine)
prod_monthly = pd.crosstab(df['order_date'], df['product_sku']).resample('M').sum()
prod_monthly = prod_monthly['2018-01':'2021-03']
items = prod_monthly.columns

# items are the names of the top20 items
test_predict = []
mse_list = []
results = pd.DataFrame()

for item in items:
    data = prod_monthly[item]
    train = np.array(data.iloc[:-3])
    test = np.array(data.iloc[-3:])

    triple = ExponentialSmoothing(train,
                                  trend="additive",
                                  seasonal="additive",
                                  seasonal_periods=12).fit(optimized=True)
    forecast = np.empty(3)
    forecast = triple.forecast(len(test))
    adj_forecast = [0 if x < 0 else int(round(x)) for x in list(forecast)]
    item_name = [item for x in range(3)]
    rmse = round(np.sqrt(mean_squared_error(test, adj_forecast[:3])), 2)
    maxe = abs(sum(test - adj_forecast[:3]))
    res = pd.DataFrame(zip(item_name, test, adj_forecast),
                       index=['m+1', 'm+2', 'm+3'], columns=['item', 'test', 'forecast'])
    res['rmse'] = ''
    res.loc['m+1', 'rmse'] = float(rmse)
    res['abs(diff)'] = ''
    res.loc['m+1', 'abs(diff)'] = maxe
    results = pd.concat([results, res], axis=0)

results = results.reset_index().rename(columns={'index': 'month'})
results.to_sql(name='top20forecasts_ExpSmoothing', con=engine, if_exists='replace', index=False)

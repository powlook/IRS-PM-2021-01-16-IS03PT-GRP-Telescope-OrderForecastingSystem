import pandas as pd

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')

df_ARIMA = pd.read_sql_table('top20forecasts_ARIMA', engine)
df_ARIMA.rename({'rmse': 'ARIMA_rmse', 'abs(diff)': 'ARIMA_maxe'}, axis=1, inplace=True)

df_SARIMA = pd.read_sql_table('top20forecasts_SARIMA', engine)
df_SARIMA.rename({'rmse': 'SARIMA_rmse', 'abs(diff)': 'SARIMA_maxe'}, axis=1, inplace=True)

df_MA = pd.read_sql_table('top20forecasts_MA', engine)
df_MA.rename({'rmse': 'MA_rmse', 'abs(diff)': 'MA_maxe'}, axis=1, inplace=True)

df_LSTM = pd.read_sql_table('top20forecasts_LSTM', engine)
df_LSTM.rename({'rmse': 'LSTM_rmse', 'abs(diff)': 'LSTM_maxe'}, axis=1, inplace=True)

# To concatenate all the 4 datasets
df_concat = pd.concat([df_ARIMA, df_SARIMA[['SARIMA_rmse', 'SARIMA_maxe']], df_MA[['MA_rmse', 'MA_maxe']], df_LSTM[['LSTM_rmse', 'LSTM_maxe']]], axis=1)
df_concat.drop(['month', 'test', 'predict'], axis=1, inplace=True)
df_concat.drop_duplicates(['item'], inplace=True)

df_concat = df_concat[['item', 'ARIMA_rmse', 'SARIMA_rmse', 'MA_rmse', 'LSTM_rmse', 'ARIMA_maxe', 'SARIMA_maxe', 'MA_maxe', 'LSTM_maxe']]

# save concat file to sql
df_concat.to_sql(name='compare_forecasts', con=engine, if_exists='replace', index=False)

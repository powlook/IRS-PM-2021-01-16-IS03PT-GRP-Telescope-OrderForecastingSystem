
import time
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Flatten, TimeDistributed
from keras.layers.convolutional import Conv1D, MaxPooling1D
from sklearn.metrics import mean_squared_error
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://iss:6Jg3bwm56xtJ2mrfNQwvsaY$@idm5peipdsus5o.crcvo0yw3sz7.ap-southeast-1.rds.amazonaws.com:3306/iss_project')


# split a univariate sequence into samples
def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)


def cnn_lstm(raw_seq):
    n_steps = 4
    # split into samples
    X, y = split_sequence(raw_seq, n_steps)
    # reshape from [samples, timesteps] into [samples, subsequences, timesteps, features]
    n_features = 1
    n_seq = 2
    n_steps = 2
    X = X.reshape((X.shape[0], n_seq, n_steps, n_features))

    # define model
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), input_shape=(None, n_steps, n_features)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit(X, y, epochs=2000, verbose=0)

    return model


df = pd.read_sql_table('orderproducts_top20', engine)
prod_monthly = pd.crosstab(df['order_date'], df['product_sku']).resample('M').sum()
prod_monthly = prod_monthly['2018-01':'2021-03']
items = prod_monthly.columns

# Forecast the last 3 month sales for the top 20 items
# items are the names of the top20 items
start_time = time.time()
results = pd.DataFrame()
for item in items:
    raw_seq = prod_monthly[item]
    model = cnn_lstm(raw_seq)
    data = raw_seq[-7:]

    preds, y_test = [], []
    for i in range(3):
        X_input = np.array(data[i:i+4])
        X_input = X_input.reshape((1, 2, 2, 1))
        pred = float(model.predict(X_input))
        adj_pred = 0 if pred < 0 else round(pred)
        preds.append(adj_pred)
        y_test.append(data[i+4])
    item_name = [item for x in range(3)]
    rmse = round(np.sqrt(mean_squared_error(y_test, preds)), 2)
    res = pd.DataFrame(zip(item_name, np.array(y_test), np.array(preds)),
                       index=['m+1', 'm+2', 'm+3'], columns=['item', 'test', 'predict'])
    res['rmse'] = ''
    res.loc['m+1', 'rmse'] = rmse
    results = pd.concat([results, res], axis=0)

results = results.reset_index().rename(columns={'index': 'month'})
results.to_sql(name='top20forecasts_LSTM', con=engine, if_exists='replace', index=False)
#results.to_csv('../data-processed/top20forecasts_LSTM_01to03.csv')

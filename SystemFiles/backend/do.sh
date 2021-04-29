#!/bin/sh
# A simple script with a function...

transform_notebook()
{
  echo "1. Start transform_notebook!!!";
  python -m nbconvert --to script /app/backend/notebooks/*.ipynb || True
  mv -f /app/backend/notebook/*.py /app/backend/ || True
  /bin/cp -f /app/backend/src/*.py /app/backend/ || True
  echo "1. Finish transform_notebook!!!";
}

data_processing()
{
  echo "2. Start data_processing!!!";
  cd /app/backend/ || True;
  ipython M_DataPreprocess.py;
  echo "2. Finish data_processing!!!";
}

do_prediction()
{
  echo "3. Start do_prediction!!!";
  cd /app/backend/ || True;
  ipython P_Forecast_top20_ARIMA.py;
  ipython P_Forecast_top20_LSTM.py;
  ipython P_Forecast_top20_RollingMA.py;
  ipython P_Forecast_top20_SARIMAX.py;
  ipython P_Forecast_Top20_ExponentialSmoothing.py;
  ipython P_orderproducts_EDA.py;
  ipython P_Introduction_to_Smoothing.py;

  ipython P_Compare_Forecasts.py;
  echo "3. Finish do_prediction!!!";
}

do_recommendation()
{
  cd /app/backend/ || True;
  echo "4. Start do_recommendation!!!"
  ipython M_Project-Process-Apriori-algorithm.py;
  ipython K_WS1toPracModule.py;
  echo "4. Finish do_recommendation!!!"
}

transform_notebook
data_processing
do_prediction
do_recommendation
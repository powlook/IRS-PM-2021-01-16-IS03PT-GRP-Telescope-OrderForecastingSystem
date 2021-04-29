# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.home.models import Order, Product, OrderProduct, ForecastArima, ForecastSarima, ForecastLSTM, ForecastRollingMA, ForecastExpSmoothing, CompareForecasts, AnalysisMBA, AnalysisMBACustomer
from flask import render_template, redirect, url_for, request, jsonify, make_response
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import json
import sqlalchemy as sa
import io
import csv

@blueprint.route('/index')
@login_required
def index():
    return render_template('dashboard.html', segment='index')

### Views
@blueprint.route('/orders', methods=['GET'])
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.paginate(page=page, per_page=10)
    return render_template( 'orders.html', orders=orders, segment='orders', title="Orders")

@blueprint.route('/products', methods=['GET'])
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=10)
    return render_template( 'products.html', products=products, segment='products', title="Products")

@blueprint.route('/inventory', methods=['GET'])
@login_required
def inventory():
    orders = Order.query.limit(5).all()
    return render_template( 'inventory.html', orders=orders, segment='inventory', title="Inventory")

@blueprint.route('/order-forecasting', methods=['GET'])
@login_required
def order_forecasting():
    forecastArima = ForecastArima.serialize_list(ForecastArima.query.all())
    forecastSarima = ForecastSarima.serialize_list(ForecastSarima.query.all())
    forecastLSTM = ForecastLSTM.serialize_list(ForecastLSTM.query.all())
    forecastRollingMA = ForecastRollingMA.serialize_list(ForecastRollingMA.query.all())
    forecastExpSmoothing = ForecastRollingMA.serialize_list(ForecastExpSmoothing.query.all())
    forecasts = {
        'recommended': forecastLSTM,
        'arima': forecastArima,
        'sarima': forecastSarima,
        'lstm': forecastLSTM,
        'rolling-ma': forecastRollingMA,
        'exp-smoothing': forecastExpSmoothing,
    }
    orderproducts = OrderProduct.group_by_product()

    formatted_op = []
    for op in orderproducts:
        p = {
            'date': op.date,
            'sku': op.product_sku,
            'qty': int(op.quantity),
        }
        formatted_op.append(p)

    return render_template('order-forecasting.html', orderproducts=formatted_op, forecasts=forecasts, segment='order-forecasting', title="Order Forecasting")

def calculate_diff(forecast):
    max = 0
    for data in forecast:
        diff = abs(data['predict'] - data['test'])
        if diff > max:
            max = diff
    return max

def calculate_rmse(forecast):
    sum = 0
    for data in forecast:
        sum += (data['predict'] - data['test']) ** 2
    
    avg = sum / len(data)
    return round(avg ** (1/2), 2)

def calculate_score(diff, rmse):
    return rmse + diff

def get_min(obj):
    min = {
        'model': '',
        'value': 100
    }
    for key, val in obj.items():
        if (val < min['value']):
            min['value'] = val
            min['model'] = key
    
    return min

def get_max(obj):
    max = {
        'model': '',
        'value': 0
    }
    for key, val in obj.items():
        if (val > max['value']):
            max['value'] = val
            max['model'] = key

    return max

@blueprint.route('/accuracy-monitoring', methods=['GET'])
@login_required
def accuracy_monitoring():
    compareForecasts = CompareForecasts.query.all()
    forecastArima = ForecastArima.serialize_list(ForecastArima.query.all())
    forecastSarima = ForecastSarima.serialize_list(ForecastSarima.query.all())
    forecastLSTM = ForecastLSTM.serialize_list(ForecastLSTM.query.all())
    forecastRollingMA = ForecastRollingMA.serialize_list(ForecastRollingMA.query.all())
    forecasts = {
        'ARIMA': forecastArima,
        'SARIMA': forecastSarima,
        'LSTM': forecastLSTM,
        'Rolling MA': forecastRollingMA
    }

    accuracy_diff = {
        'ARIMA': calculate_diff(forecastArima),
        'SARIMA': calculate_diff(forecastSarima),
        'LSTM': calculate_diff(forecastLSTM),
        'Rolling MA': calculate_diff(forecastRollingMA)
    }

    accuracy_rmse = {
        'ARIMA': calculate_rmse(forecastArima),
        'SARIMA': calculate_rmse(forecastSarima),
        'LSTM': calculate_rmse(forecastLSTM),
        'Rolling MA': calculate_rmse(forecastRollingMA)
    }

    accuracy_overall = {
        'ARIMA': calculate_score(accuracy_diff['ARIMA'], accuracy_rmse['ARIMA']),
        'SARIMA':  calculate_score(accuracy_diff['SARIMA'], accuracy_rmse['SARIMA']),
        'LSTM': calculate_score(accuracy_diff['LSTM'], accuracy_rmse['LSTM']),
        'Rolling MA': calculate_score(accuracy_diff['Rolling MA'], accuracy_rmse['Rolling MA'])
    }  

    recommended = {
        'DIFF': get_min(accuracy_diff),
        'RMSE': get_min(accuracy_rmse),
        'OVERALL': get_min(accuracy_overall),
    }

    return render_template('accuracy-monitoring.html',
        forecasts=forecasts,
        compareForecasts=compareForecasts,
        accuracy_diff=accuracy_diff,
        accuracy_rmse=accuracy_rmse,
        recommended=recommended,
        segment='accuracy-monitoring',
        title="Accuracy Monitoring")

@blueprint.route('/analysis-mba', methods=['GET'])
@login_required
def analysis_mba():
    page = request.args.get('page', 1, type=int)
    mba_items = AnalysisMBA.query.all()
    mba_customers_paginate = AnalysisMBACustomer.query.filter(AnalysisMBACustomer.recommended_sku != "[]").paginate(page=page, per_page=10)

    formatted_mba_customers = []
    for c in mba_customers_paginate.items:
        recommend_arr = json.loads(c.recommended_sku)
        recommend_arr = recommend_arr[:3]
        recommend_arr = list(map(lambda x: (x[0] + " <small class=\"text-success\">(" + str(round(x[1] * 100, 2)) + ")</small>"), recommend_arr))

        line_items_arr = json.loads(c.line_items_sku)[:3]

        customer = {
            'customer_id': c.customer_id,
            'bought': ", ".join(line_items_arr),
            'recommend': ", ".join(recommend_arr),
        }
        formatted_mba_customers.append(customer)

    return render_template('analysis-mba.html',
        segment='analysis-mba',
        analysis_items = mba_items,
        analysis_customer_pagination = mba_customers_paginate,
        analysis_customer = formatted_mba_customers,
        title="Market Basket Analysis")

### API
@blueprint.route('/api/forecasts/csv', methods=['GET'])
@login_required
def api_export_forecasts():
    forecast = request.args.get('forecast')
    if forecast == 'arima':
        forecast_list = ForecastArima.serialize_list(ForecastArima.query.all())
    elif forecast == 'sarima':
        forecast_list = ForecastSarima.serialize_list(ForecastSarima.query.all())
    elif forecast == 'rolling-ma':
        forecast_list = ForecastRollingMA.serialize_list(ForecastRollingMA.query.all())
    elif forecast == 'exp-smoothing':
        forecast_list = ForecastExpSmoothing.serialize_list(ForecastExpSmoothing.query.all())
    else:
        forecast_list = ForecastLSTM.serialize_list(ForecastLSTM.query.all())
    
    forecast_list = map(lambda x: x.values(), forecast_list)

    formatted_data = [['SKU', 'Date', 'Prediction', 'Actual']]
    for d in forecast_list:
        arr = list(d)[0:4]
        date = '2021-01'
        if arr[0] == 'm+2':
            date = '2021-02'
        elif arr[0] == 'm+3':
            date = '2021-03'
        elif arr[0] == 'm+4':
            date = '2021-04'
        result = [arr[3], date, arr[2], arr[1]]
        formatted_data.append(result)

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(formatted_data)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export" + forecast + ".csv"
    output.headers["Content-type"] = "text/csv"
    return output

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

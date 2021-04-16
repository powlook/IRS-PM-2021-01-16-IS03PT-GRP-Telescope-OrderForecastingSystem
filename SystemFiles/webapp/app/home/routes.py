# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.home.models import Order, Product, OrderProduct, ForecastArima, ForecastSarima, ForecastLSTM, ForecastRollingMA
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import sqlalchemy as sa

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
    forecasts = {
        'recommended': forecastLSTM,
        'arima': forecastArima,
        'sarima': forecastSarima,
        'lstm': forecastLSTM,
        'rolling-ma': forecastRollingMA
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
        diff = abs(data['predict'])
        if diff > max:
            max = diff
    return max

def calculate_score(diff, rmse):
    return rmse - diff

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
        'ARIMA': 3,
        'SARIMA': 2,
        'LSTM': 15,
        'Rolling MA': 2
    }

    accuracy_overall = {
        'ARIMA': calculate_score(accuracy_diff['ARIMA'], accuracy_rmse['ARIMA']),
        'SARIMA':  calculate_score(accuracy_diff['SARIMA'], accuracy_rmse['SARIMA']),
        'LSTM': calculate_score(accuracy_diff['LSTM'], accuracy_rmse['LSTM']),
        'Rolling MA': calculate_score(accuracy_diff['Rolling MA'], accuracy_rmse['Rolling MA'])
    }  

    recommended = {
        'DIFF': get_min(accuracy_diff),
        'RMSE': get_max(accuracy_rmse),
        'OVERALL': get_max(accuracy_overall),
    }

    return render_template('accuracy-monitoring.html',
        forecasts=forecasts,
        accuracy_diff=accuracy_diff,
        accuracy_rmse=accuracy_rmse,
        recommended=recommended,
        segment='accuracy-monitoring',
        title="Accuracy Monitoring")


### API
@blueprint.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    orders = Order.query.limit(5).all()
    return jsonify(Order.serialize_list(orders))
    # return jsonify({ 'order_id': 1, 'name': 'ABC' }, { 'order_id': 2, 'name': 'CDEF' })

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

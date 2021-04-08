# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.home.models import Order, OrderProduct, ForecastArima
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
    orders = Order.query.limit(5).all()
    return render_template( 'orders.html', orders=orders, segment='orders')

@blueprint.route('/products', methods=['GET'])
@login_required
def products():
    orders = Order.query.limit(5).all()
    return render_template( 'products.html', orders=orders, segment='products')

@blueprint.route('/inventory', methods=['GET'])
@login_required
def inventory():
    orders = Order.query.limit(5).all()
    return render_template( 'inventory.html', orders=orders, segment='inventory')

@blueprint.route('/smart-procurement', methods=['GET'])
@login_required
def smart_procurement():
    forecasts = ForecastArima.query.all()
    orderproducts = OrderProduct.group_by_product()

    dates = []
    skus = []
    original = []
    for op in orderproducts:
        dates.append(op.date)
        skus.append(op.product_sku)
        original.append(op)

    dates = sorted(list(set(dates)))
    skus = sorted(list(set(skus)))

    emptyList = [0] * len(dates)
    productDict = dict.fromkeys(skus, [0] * len(dates))

    for ab in original:
        try:
            index = dates.index(ab.date)
            curr_arr = productDict[ab.product_sku].copy()
            curr_arr[index] = int(ab.quantity)
            sku = ab.product_sku
            productDict.update({ sku: curr_arr })
        except:
            return

    return render_template( 'smart-procurement.html', forecasts=forecasts, productdict=productDict, dates=dates, segment='smart-procurement')


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

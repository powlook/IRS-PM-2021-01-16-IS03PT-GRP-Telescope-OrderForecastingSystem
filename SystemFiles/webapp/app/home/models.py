# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Binary, Column, Integer, String, DateTime, Float, Text, text
from sqlalchemy.inspection import inspect

from app import db

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Order(db.Model, Serializer):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    total_price = Column(Float)
    line_items = Column(Text)

    def __repr__(self):
        return str(self.id)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class Product(db.Model, Serializer):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    sku = Column(Text)
    price_usd = Column(Float)
    category = Column(Text)
    tags = Column(Text)
    created_at = Column(DateTime)

    def __repr__(self):
        return str(self.id)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class OrderProduct(db.Model, Serializer):
    __tablename__ = 'orders_products_v2'

    product_sku =  Column(Text, primary_key=True)
    product_quantity =  Column(Integer)
    order_id =  Column(Integer)
    order_date =  Column(DateTime, primary_key=True)

    def __repr__(self):
        return str(self.product_sku + '_' + str(self.order_id))

    def serialize(self):
        d = Serializer.serialize(self)
        return d

    def group_by_product():
        query = text("SELECT DATE_FORMAT(order_date, '%Y-%m') AS date, product_sku, SUM(product_quantity) AS quantity FROM orders_products_v2 WHERE product_sku IN (SELECT DISTINCT(item) FROM top20forecasts_ARIMA) GROUP BY `date`, product_sku")
        d = db.engine.execute(query)
        return d

class ForecastArima(db.Model, Serializer):
    __tablename__ = 'top20forecasts_ARIMA'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)
    rmse = Column(String)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

    def format():
        query = text("SELECT * from top20forecasts_ARIMA LIMIT :limit")
        d = db.engine.execute(query, limit=5)
        return d


class ForecastSarima(db.Model, Serializer):
    __tablename__ = 'top20forecasts_SARIMA'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)
    rmse = Column(String)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class ForecastRollingMA(db.Model, Serializer):
    __tablename__ = 'top20forecasts_MA'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)
    rmse = Column(String)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class ForecastLSTM(db.Model, Serializer):
    __tablename__ = 'top20forecasts_LSTM'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)
    rmse = Column(String)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class ForecastExpSmoothing(db.Model, Serializer):
    __tablename__ = 'top20forecasts_ExpSmoothing'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)
    rmse = Column(String)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class CompareForecasts(db.Model, Serializer):
    __tablename__ = 'compare_forecasts'

    item = Column(Text, primary_key=True)
    ARIMA_rmse = Column(Text)
    SARIMA_rmse = Column(Text)
    MA_rmse = Column(Text)
    ExpSm_rmse = Column(Text)
    LSTM_rmse = Column(Text)
    ARIMA_maxe = Column(Text)
    SARIMA_maxe = Column(Text)
    MA_maxe = Column(Text)
    ExpSm_maxe = Column(Text)
    LSTM_maxe = Column(Text)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class AnalysisMBA(db.Model, Serializer):
    __tablename__ = 'combo_recommended_table'

    LHS = Column(Text, primary_key=True)
    RHS = Column(Text, primary_key=True)
    Confidence = Column(Float)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

class AnalysisMBACustomer(db.Model, Serializer):
    __tablename__ = 'customer_recommended_table'

    customer_id = Column(Text, primary_key=True)
    recommended_sku = Column(Text)
    line_items_sku = Column(Text)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d
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
        query = text("SELECT DATE_FORMAT(order_date, '%Y-%m') AS date, product_sku, SUM(product_quantity) AS quantity FROM orders_products_v2 WHERE order_date >= '2020-01-01' and order_date <= '2020-12-31' and product_sku IN (SELECT DISTINCT(item) FROM top20forecasts_ARIMA) GROUP BY `date`, product_sku")
        d = db.engine.execute(query)
        return d

class ForecastArima(db.Model, Serializer):
    __tablename__ = 'top20forecasts_ARIMA'

    month = Column(Text, primary_key=True)
    test = Column(Integer)
    predict = Column(Integer)
    item = Column(Text, primary_key=True)

    def __repr__(self):
        return str(self.month + '_' + self.item)

    def serialize(self):
        d = Serializer.serialize(self)
        return d

    def format():
        query = text("SELECT * from top20forecasts_ARIMA LIMIT :limit")
        d = db.engine.execute(query, limit=5)
        return d


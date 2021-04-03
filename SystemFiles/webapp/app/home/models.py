# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from sqlalchemy import Binary, Column, Integer, String, DateTime, Float, Text
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

from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    JSON
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Order(Base):
    __tablename__ = 'order'
    id = Column(String, primary_key=True)
    owner_id = Column(Integer)
    price = Column(Numeric)
    amount = Column(Numeric)
    type = Column(String)

    def toDict(self):
        return {"id":self.id, "owner_id":self.owner_id, "price":float(self.price), "amount":float(self.amount), "type":self.type}

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    balance = Column(Numeric)
    stuff = Column(Numeric)

    def toDict(self):
        return {"id":self.id, "name":self.name, "balance":float(self.balance), "stuff":float(self.stuff)}

class OrderBookStorage(Base):
    __tablename__ = 'orderbookstorage'
    id = Column(Integer, primary_key=True)
    asks = Column(JSON)
    bids = Column(JSON)

class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
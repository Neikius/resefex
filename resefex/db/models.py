from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
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
    id = Column(Integer, primary_key=True)
    price = Column(Numeric)
    amount = Column(Numeric)


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
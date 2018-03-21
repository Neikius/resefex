import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from .models import (
    DBSession,
    Base,
    User, OrderBookStorage)

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        if DBSession.query(User).filter_by(id=1).first() == None:
            user1 = User(id=1, balance=10.0, stuff=10.0, name="user1")
            DBSession.add(user1)
        if DBSession.query(User).filter_by(id=2).first() == None:
            user2 = User(id=2, balance=15.0, stuff=0.0, name="user2")
            DBSession.add(user2)
        if DBSession.query(OrderBookStorage).first() == None:
            orderBook = OrderBookStorage(id=1, asks=[], bids=[])
            DBSession.add(orderBook)
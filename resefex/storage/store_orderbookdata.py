import sys

import transaction
from kafka import KafkaConsumer
import json

from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config

from resefex import DBSession
from resefex.db.models import OrderBookStorage
from resefex.db.orderbook import OrderBook


def main(argv=sys.argv):
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    storeData = StoreOrderBookData()

class StoreOrderBookData:
    consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                             value_deserializer=lambda v: json.loads(v))

    def __init__(self):
        while(1):
            with transaction.manager:
                self.consumer.subscribe(['orderbook'])
                records = self.consumer.poll(1000)
                orderbook = {}
                for key in records:
                    for record in records[key]:
                        orderbook = OrderBook(json.loads(record.value))

                storage: OrderBookStorage = DBSession.query(OrderBookStorage).filter_by(id=1).one()
                storage.asks = orderbook.asks
                storage.bids = orderbook.bids

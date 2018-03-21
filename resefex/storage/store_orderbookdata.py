import logging
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
    storeData = StoreOrderBookData(settings['kafka.url'])

class StoreOrderBookData:

    log = logging.getLogger(__name__)

    consumer: KafkaConsumer

    def __init__(self, kafka_url: str):
        self.log.info("Initialized with kafka_url=" + kafka_url)
        self.consumer = KafkaConsumer(bootstrap_servers=kafka_url,
                                 value_deserializer=lambda v: json.loads(v))

        self.consumer.subscribe(['orderbook'])
        self.log.debug("Init OK")
        while(1):
            with transaction.manager:
                self.log.debug("Polling records")
                records = self.consumer.poll(1000)
                orderbook = None
                for key in records:
                    self.log.debug("Got " + str(len(records[key])) + " records")
                    for record in records[key]:
                        orderbook = OrderBook(json.loads(record.value))

                if orderbook != None:
                    self.log.debug("Got latest orderbook=" + repr(orderbook))
                    storage: OrderBookStorage = DBSession.query(OrderBookStorage).filter_by(id=1).one()
                    storage.asks = orderbook.asks
                    storage.bids = orderbook.bids
                    self.log.debug("Stored latest orderbook status")

import json
import logging

import sys

import transaction
from kafka import KafkaConsumer

from resefex.db.models import User, DBSession

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from sqlalchemy import engine_from_config


def main(argv=sys.argv):
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    storeBalance = StoreBalance(settings['kafka.url'])

class StoreBalance:

    log = logging.getLogger(__name__)

    consumer: KafkaConsumer

    def __init__(self, kafka_url: str):
        self.log.info("Init with kafka_url " + kafka_url)
        self.consumer = KafkaConsumer(bootstrap_servers=kafka_url,
                      value_deserializer=lambda v: json.loads(v))
        self.consumer.subscribe(['balance_update'])
        self.log.debug("Init OK")
        self.loop()

    def loop(self):
        while (1):
            self.log.debug("Polling data")
            topics = self.consumer.poll(1000)

            for topic in topics:
                self.log.debug("Got data " + str(len(topics[topic])) + " records")
                for record in topics[topic]:
                    self.log.info("Updating balance for " + repr(record.value))
                    self.update_balance(record.value)

    def update_balance(self, data):
        with transaction.manager:
            self.log.debug("Looking up bid user id=" + repr(data['bid_user']) + " and aks user id=" + repr(data['ask_user']))
            bid_user = DBSession.query(User).filter_by(id=data['bid_user']).one()
            ask_user = DBSession.query(User).filter_by(id=data['ask_user']).one()

            self.log.debug("Bid user old stuff status: " + repr(bid_user.stuff) + " ask user old balance status: " + repr(ask_user.balance))
            bid_user.stuff = float(bid_user.stuff) + data['amount']
            ask_user.balance = float(ask_user.balance) + data['amount'] * data['price']
            self.log.debug("Bid user new stuff status: " + repr(bid_user.stuff) + " ask user new balance status: " + repr(ask_user.balance))

import json

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
    storeBalance = StoreBalance()

class StoreBalance:

    consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                             value_deserializer=lambda v: json.loads(v))

    def __init__(self):
        self.consumer.subscribe(['balance_update'])
        self.loop()

    def loop(self):
        while (1):
            topics = self.consumer.poll(100)
            for topic in topics:
                for record in topics[topic]:
                    self.update_balance(record.value)

    def update_balance(self, data):
        with transaction.manager:
            bidUser = DBSession.query(User).filter_by(id=data['bid_user']).one()
            askUser = DBSession.query(User).filter_by(id=data['ask_user']).one()

            bidUser.stuff = float(bidUser.stuff) + data['amount']
            askUser.balance = float(askUser.balance) + data['amount'] * data['price']

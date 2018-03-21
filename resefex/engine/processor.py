import logging
import json

import sys
from kafka import KafkaConsumer, KafkaProducer
from pyramid.paster import get_appsettings, setup_logging

from resefex.db.orderbook import OrderBook, OrderBookEntry

def main(argv=sys.argv):
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    orderBookProcessor = OrderBookProcessor(settings['kafka.url'])

class OrderBookProcessor:

    log = logging.getLogger(__name__)

    consumer: KafkaConsumer
    producer: KafkaProducer

    orderbook = OrderBook()

    def __init__(self, kafka_url: str):
        # load orderbook data

        self.log.info("Init with kafka_url " + kafka_url)
        self.consumer = KafkaConsumer(bootstrap_servers=kafka_url,
                                 value_deserializer=lambda v: json.loads(v))

        self.producer = KafkaProducer(bootstrap_servers=kafka_url,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))

        self.consumer.subscribe(topics=['limit_order'])
        self.loop()

    def loop(self):
        while(1):
            self.log.debug("Fetching records")
            records = self.consumer.poll(timeout_ms=1000)
            self.log.debug("Fetched records " + repr(records))
            self.process_record(records)

    def process_record(self, records: dict):
        if len(records) < 1:
            return
        for key in records:
            for record in records[key]:
                entry = OrderBookEntry(record.value)
                if entry.operation == 'REMOVE':
                    self.log.info("Processing order removal id="+entry.id)
                    self.orderbook.remove(entry.type, entry.id)
                elif entry.operation == 'ADD':
                    self.log.info("Processing order add order="+entry.toJSON())
                    self.orderbook.add(entry.type, entry)

                self.log.debug("InternalOrderbook:" + self.orderbook.toJSON())
                self.process_orderbook(self.orderbook)

    def process_orderbook(self, orderbook: OrderBook):
        if orderbook.isEmpty():
            return
        top_bid = orderbook.topBid()
        top_ask = orderbook.topAsk()

        while top_bid.price >= top_ask.price:
            self.log.debug("Executing orders bid=" + repr(top_bid) + " ask=" + repr(top_ask))
            self.execute_orders(orderbook, top_bid, top_ask)

            top_bid = orderbook.topBid()
            top_ask = orderbook.topAsk()

        self.log.debug("Sending orderbook update")
        self.push_orderbook(orderbook)

    def execute_orders(self, orderbook: OrderBook, top_bid: OrderBookEntry, top_ask: OrderBookEntry):
        if top_bid.amount > top_ask.amount:
            self.log.debug("Processing order")
            amount = top_bid.amount - top_ask.amount
            new_top_bid_amount = top_bid.amount - amount
            balance_update = {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": amount,
                "price": top_bid.price
            }
            self.producer.send('balance_update', balance_update)
            top_bid.amount = new_top_bid_amount
            orderbook.remove("ASK", top_ask.id)
        elif top_bid.amount < top_ask.amount:
            amount = top_ask.amount - top_bid.amount
            new_top_ask_amount = top_ask.amount - amount
            balance_update = {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": amount,
                "price": top_bid.price
            }
            self.producer.send('balance_update', balance_update)
            top_ask.amount = new_top_ask_amount
            orderbook.remove("BID", top_bid.id)
        else:
            print("Send order execution data ")
            balance_update = {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": top_bid.amount,
                "price": top_bid.price
            }
            self.producer.send('balance_update', balance_update)
            orderbook.remove("ASK", top_ask.id)
            orderbook.remove("BID", top_bid.id)

    def push_orderbook(self, orderbook):
        self.producer.send('orderbook', orderbook.toJSON())
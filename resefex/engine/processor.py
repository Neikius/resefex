import jsonpickle
import json

import sys
from kafka import KafkaConsumer, KafkaProducer

from resefex.db.orderbook import OrderBook, OrderBookEntry

def main(argv=sys.argv):
    orderBookProcessor = OrderBookProcessor()

class OrderBookProcessor:
    consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                             value_deserializer=lambda v: json.loads(v))
#                             value_deserializer=lambda v: jsonpickle.decode(v))

    producer = KafkaProducer(bootstrap_servers='10.52.52.100:9092',
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
#                             value_serializer=lambda v: jsonpickle.encode(v).encode('utf-8'))


    orderbook = OrderBook()

    def __init__(self):
        self.consumer.subscribe(topics=['limit_order'])
        self.loop()

    def loop(self):
        while(1):
            records = self.consumer.poll(timeout_ms=500)
            print("Record:" + repr(records))
            self.process_record(records)

            print("InternalOrderbook:" + self.orderbook.toJSON())
            self.process_orderbook(self.orderbook)

    def process_record(self, records: dict):
        if len(records) < 1:
            return
        for key in records:
            for record in records[key]:
                entry = OrderBookEntry(record.value)
                if entry.operation == 'REMOVE':
                    self.orderbook.remove(entry.type, entry.id)
                elif entry.operation == 'ADD':
                    self.orderbook.add(entry.type, entry)

    def process_orderbook(self, orderbook: OrderBook):
        if orderbook.isEmpty():
            return
        top_bid = orderbook.topBid()
        top_ask = orderbook.topAsk()

        while top_bid.price >= top_ask.price:
            self.execute_orders(orderbook, top_bid, top_ask)

            top_bid = orderbook.topBid()
            top_ask = orderbook.topAsk()

        self.push_orderbook(orderbook)

    def execute_orders(self, orderbook: OrderBook, top_bid: OrderBookEntry, top_ask: OrderBookEntry):
        if top_bid.amount > top_ask.amount:
            amount = top_bid.amount - top_ask.amount
            new_top_bid_amount = top_bid.amount - amount
            self.producer.send('balance_update', {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": amount,
                "price": top_bid.price
            })
            top_bid.amount = new_top_bid_amount
            orderbook.remove("ASK", top_ask.id)
        elif top_bid.amount < top_ask.amount:
            amount = top_ask.amount - top_bid.amount
            new_top_ask_amount = top_ask.amount - amount
            self.producer.send('balance_update', {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": amount,
                "price": top_bid.price
            })
            top_ask.amount = new_top_ask_amount
            orderbook.remove("BID", top_bid.id)
        else:
            print("Send order execution data ")
            self.producer.send('balance_update', {
                "bid_user": top_bid.owner_id,
                "ask_user": top_ask.owner_id,
                "amount": top_bid.amount,
                "price": top_bid.price
            })
            orderbook.remove("ASK", top_ask.id)
            orderbook.remove("BID", top_bid.id)

    def push_orderbook(self, orderbook):
        self.producer.send('orderbook', self.orderbook.toJSON())
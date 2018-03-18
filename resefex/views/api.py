import json
from uuid import uuid4

import transaction
from cornice import Service
from kafka import KafkaProducer, KafkaConsumer
from pyramid.request import Request

from resefex import DBSession
from resefex.db.models import OrderBookStorage, User

place_limit_order = Service(name='place_limit_order', path='/api/v1/order/limit/{type}/{amount}/{price}', cors_origins=('*',))
order = Service(name='order_remove', path='/api/v1/order/{id}', cors_origins=('*',))
orders = Service(name='orders', path='/api/v1/orders', cors_origins=('*',))
orderbook = Service(name='orderbook', path='/api/v1/orderbook', cors_origins=('*',))
orderbook_asks = Service(name='orderbook_asks', path='/api/v1/orderbook/asks', cors_origins=('*',))
orderbook_bids = Service(name='orderbook_bids', path='/api/v1/orderbook/bids', cors_origins=('*',))

producer = KafkaProducer(bootstrap_servers='10.52.52.100:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                         value_deserializer=lambda v: json.loads(v))

@place_limit_order.put()
def put_place_limit_order(request: Request):
    #let's abuse bearer auth for now
    if (request.authorization is None):
        return {"error": "no auth"}
    else:
        user_id = int(request.authorization.params)
    amount = float(request.matchdict['amount'])
    price = float(request.matchdict['price'])
    type = request.matchdict['type']
    with transaction.manager:
        user = DBSession.query(User).filter_by(id=user_id).one()
        if type == "ASK":
            if user.stuff >= amount:
                user.stuff = float(user.stuff) - amount
            else:
                return None
        elif type == "BID":
            if user.balance >= price*amount:
                user.balance = float(user.balance) - price*amount
            else:
                return None
        order = {"id": str(uuid4()), "amount": amount, "price": price, "operation": "ADD", "type": type, "owner_id": user_id}
        producer.send(topic='limit_order', value=order)
        return order

@order.delete()
def delete_order(request):
    id = request.matchdict['id']
    print("Requested removal of order " + id)
    return

@order.get()
def get_order_details(request):
    id = request.matchdict['id']
    print("Requested order id " + id + " details")
    return {"id": 1, "price": 1, "amount": 1}

@orders.get()
def get_all_orders(request):
    print("Requested all orders")
    orders = []
    return orders

@orderbook.get()
def get_orderbook(request):
    consumer.subscribe(['orderbook'])
    records = consumer.poll(100, max_records=1)
    for key in records:
        return records[key][0].value

@orderbook_asks.get()
def get_orderbook(request):
    return DBSession.query(OrderBookStorage).one().asks

@orderbook_bids.get()
def get_orderbook(request):
    return DBSession.query(OrderBookStorage).one().bids


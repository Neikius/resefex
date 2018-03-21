import json
import logging
from uuid import uuid4

import transaction
from cornice import Service
from kafka import KafkaProducer, KafkaConsumer
from pyramid.request import Request

from jwkest.jws import JWSig
from jwkest.jwt import JWT
from resefex import DBSession
from resefex.db.models import OrderBookStorage, User, Order

log = logging.getLogger(__name__)

place_limit_order = Service(name='place_limit_order', path='/api/v1/order/limit/{type}/{amount}/{price}', cors_origins=('*',))
order = Service(name='order_remove', path='/api/v1/order/{id}', cors_origins=('*',))
orders = Service(name='orders', path='/api/v1/orders', cors_origins=('*',))
orderbook = Service(name='orderbook', path='/api/v1/orderbook', cors_origins=('*',))
orderbook_asks = Service(name='orderbook_asks', path='/api/v1/orderbook/asks', cors_origins=('*',))
orderbook_bids = Service(name='orderbook_bids', path='/api/v1/orderbook/bids', cors_origins=('*',))
user_details = Service(name='user_details', path='/api/v1/user/details', cors_origins=('*',))
user_orders = Service(name='user_orders', path='/api/v1/user/orders', cors_origins=('*',))

@place_limit_order.put()
def put_place_limit_order(request: Request):

    user = map_user(request)
    if user == None:
        return {"error": "no auth"}
    else:
        user_id = user.id
    amount = float(request.matchdict['amount'])
    price = float(request.matchdict['price'])
    type = request.matchdict['type']
    log.debug("New order for data:" + json.dumps({"amount":amount, "price":price, "type":type, "owner_id":user_id}))
    with transaction.manager:
        user = DBSession.query(User).filter_by(id=user_id).one()
        if type == "ASK":
            if user.stuff >= amount:
                user.stuff = float(user.stuff) - amount
            else:
                log.debug("User does not have enough stuff")
                return None
        elif type == "BID":
            if user.balance >= price*amount:
                user.balance = float(user.balance) - price*amount
            else:
                log.debug("User does not have enough funds")
                return None
        order = {"id": str(uuid4()), "amount": amount, "price": price, "operation": "ADD", "type": type, "owner_id": user_id}
        producer: KafkaProducer = request.registry.kafka_producer
        log.debug("Placing order into queue" + json.dumps(order))
        producer.send(topic='limit_order', value=order)
        log.debug("Order successfully placed in the queue")
        return order

@order.delete()
def delete_order(request):
    # TODO Verify user
    id = request.matchdict['id']
    log.debug("Requested removal of order " + id)
    return

@order.get()
def get_order_details(request):
    id = request.matchdict['id']
    log.debug("Requested order id " + id + " details")
    return {"id": 1, "price": 1, "amount": 1}

@orders.get()
def get_all_orders(request):
    log.error("Requested all orders - not implemented!")
    orders = []
    return orders

@orderbook.get()
def get_orderbook(request):
    log.warning("Requested full orderbook - this method reads from MQ 1 by 1 and won't return the actual latest value")
    consumer: KafkaConsumer = request.registry.kafka_consumer
    consumer.subscribe(['orderbook'])
    records = consumer.poll(100, max_records=1)
    for key in records:
        return records[key][0].value

@orderbook_asks.get()
def get_orderbook(request):
    log.debug("Requested ASK orderbooks")
    return DBSession.query(OrderBookStorage).one().asks

@orderbook_bids.get()
def get_orderbook(request):
    log.debug("Requested BID orderbooks")
    return DBSession.query(OrderBookStorage).one().bids

@user_details.get()
def get_user_details(request):
    user = map_user(request)
    if user == None:
        return {"error": "no auth"}
    else:
        user_id = user.id
    user = DBSession.query(User).filter_by(id=user_id).one()
    return user.toDict()

@user_orders.get()
def get_user_orders(request):
    user = map_user(request)
    if user == None:
        return {"error": "no auth"}
    else:
        user_id = user.id
    orders = DBSession.query(Order).filter_by(user_id=user_id).all()
    orders_array = []
    for order in orders:
        orders_array.append(order.toDict())
    return orders_array

def map_user(request):
    if (request.authorization is not None):
        if (JWSig().unpack(request.authorization.params).valid()):
            username = JWT().unpack(request.authorization.params).payload()['preferred_username']
            #map username to userid
            user = DBSession.query(User).filter_by(name=username).first()
            return user
    return None
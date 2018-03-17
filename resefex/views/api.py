import json
from uuid import uuid4

from cornice import Service
from kafka import KafkaProducer, KafkaConsumer

place_limit_order = Service(name='place_limit_order', path='/api/v1/order/limit/{type}/{amount}/{price}')
order = Service(name='order_remove', path='/api/v1/order/{id}')
orders = Service(name='orders', path='/api/v1/orders')
orderbook = Service(name='orderbook', path='/api/v1/orderbook')

producer = KafkaProducer(bootstrap_servers='10.52.52.100:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))
consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                         value_deserializer=lambda v: json.loads(v))

id = 1

@place_limit_order.put()
def put_place_limit_order(request):
    amount = float(request.matchdict['amount'])
    price = float(request.matchdict['price'])
    type = request.matchdict['type']
    order = {"id": str(uuid4()), "amount": amount, "price": price, "operation": "ADD", "type": type}
    producer.send(topic='limit_order', value=order)
    print("Order placed with amount:" + repr(amount) + " price: " + repr(price))
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
    orderbook = consumer.poll(100, max_records=1)
    return orderbook

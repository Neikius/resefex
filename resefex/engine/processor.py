import jsonpickle
from kafka import KafkaConsumer, KafkaProducer

class OrderBook:
    id: str
    price: float
    amount: float
    type: str
    operation: str

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

class OrderBookProcessor:
    consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092',
                             value_deserializer=lambda v: jsonpickle.decode(v))
#                             value_deserializer=lambda v: json.loads(v))
    producer = KafkaProducer(bootstrap_servers='10.52.52.100:9092',
                             value_serializer=lambda v: jsonpickle.encode(v).encode('utf-8'))
#                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    orderbook = dict()

    def __init__(self):
        self.consumer.subscribe(topics=['limit_order'])
        self.loop()

    def loop(self):
        while(1):
            records = self.consumer.poll(timeout_ms=1000, max_records=1)
            print("Record:" + repr(records))
            self.process_record(records)

            print("InternalOrderbook:" + jsonpickle.encode(self.orderbook))
            self.process_orderbook(self.orderbook)

    def process_record(self, records: dict):
        if len(records) < 1:
            return
        for key in records:
            record = OrderBook(records[key][0].value)
            if record.operation == 'REMOVE':
                del self.orderbook[record.id]
            elif record.operation == 'ADD':
                self.orderbook[record.id] = record

    def process_orderbook(self, orderbook: dict):
        if len(orderbook) < 1:
            return
        top_bid = self.top_bid(orderbook)
        top_ask = self.top_ask(orderbook)

        while top_bid.price >= top_ask.price:
            self.execute_orders(orderbook, top_bid, top_ask)

            top_bid = self.top_bid(orderbook)
            top_ask = self.top_ask(orderbook)

        self.push_orderbook(orderbook)

    def execute_orders(self, orderbook, top_bid, top_ask):
        print("TODO execute balance changes")

        if top_bid.amount > top_ask.amount:
            orderbook[top_bid.id].amount -= top_ask.amount
            del orderbook[top_ask.id]
        elif top_bid.amount < top_ask.amount:
            orderbook[top_ask.id].amount -= top_bid.amount
            del orderbook[top_bid.id]
        else:
            del orderbook[top_ask.id]
            del orderbook[top_bid.id]

    def top_bid(self, orderbook: dict):
        top = OrderBook({"price":float('0')})
        for i in orderbook.keys():
            if orderbook[i].type == "BID" and orderbook[i].price > top.price:
                top = orderbook[i]
        return top

    def top_ask(self, orderbook):
        top = OrderBook({"price":float('inf')})
        for i in orderbook.keys():
            if orderbook[i].type == "ASK" and orderbook[i].price < top.price:
                top = orderbook[i]
        return top

    def push_orderbook(self, orderbook):
        self.producer.send('orderbook', self.orderbook)
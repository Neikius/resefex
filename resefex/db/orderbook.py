import json


class OrderBook:
    bids: dict = dict()
    asks: dict = dict()

    def toArray(self, d: dict):
        a = []
        for it in d.values():
            a.append(it.toDict())
        return a

    def toDict(self):
        return {"bids": self.toArray(self.bids), "asks": self.toArray(self.asks)}

    def toJSON(self):
        return json.dumps(self.toDict())

    def getAsksJON(self):
        return json.dumps(self.toArray(self.asks))

    def getBidsJSON(self):
        return json.dumps(self.toArray(self.bids))

    def isEmpty(self):
        if len(self.bids) + len(self.asks) < 0:
            return True
        else:
            return False

    def remove(self, type, id):
        if type == "BID":
            del self.bids[id]
        elif type == "ASK":
            del self.asks[id]

    def add(self, type, record):
        if type == "BID":
            self.bids[record.id] = record
        elif type == "ASK":
            self.asks[record.id] = record

    def topBid(self):
        top = OrderBookEntry({"price":float('0')})
        for i in self.bids.keys():
            if self.bids[i].price > top.price:
                top = self.bids[i]
        return top

    def topAsk(self):
        top = OrderBookEntry({"price":float('inf')})
        for i in self.asks.keys():
            if self.asks[i].price < top.price:
                top = self.asks[i]
        return top

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class OrderBookEntry:
    id: str
    price: float
    amount: float
    type: str
    operation: str
    owner_id: int

    def toDict(self):
        return {"id": self.id, "price": self.price, "amount": self.amount, "type": self.type, "operation": self.operation, \
                "owner_id": self.owner_id}

    def toJSON(self):
        return json.dumps(self.toDict())

    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

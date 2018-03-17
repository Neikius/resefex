from kafka import KafkaConsumer


class Test:
    def __init__(self):
        consumer = KafkaConsumer(bootstrap_servers='10.52.52.100:9092')
        consumer.subscribe(topics=['limit_order'])
        while(1):
            record = consumer.poll(timeout_ms=100, max_records=1)
            print("Record:" + repr(record))
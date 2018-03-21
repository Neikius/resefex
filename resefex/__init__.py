from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from resefex.db.models import DBSession, Base

import json

from kafka import KafkaProducer, KafkaConsumer


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    producer = KafkaProducer(bootstrap_servers=settings['kafka.url'],
                             value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    consumer = KafkaConsumer(bootstrap_servers=settings['kafka.url'],
                             value_deserializer=lambda v: json.loads(v))

    config = Configurator(settings=settings,
                          root_factory='resefex.db.models.Root')
    config.registry.kafka_producer = producer
    config.registry.kafka_consumer = consumer

    config.include('pyramid_chameleon')
    config.include('cornice')
    config.add_route('home', '/')
    config.scan('.views')
    return config.make_wsgi_app()

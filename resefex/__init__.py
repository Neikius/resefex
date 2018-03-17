from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from resefex.db.models import DBSession, Base


def main(global_config, **settings):
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          root_factory='resefex.db.models.Root')
    config.include('pyramid_chameleon')
    config.include('cornice')
    config.add_route('home', '/')
    config.scan('.views')
    return config.make_wsgi_app()

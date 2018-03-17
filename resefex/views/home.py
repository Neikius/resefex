from pyramid.view import view_config, view_defaults


@view_defaults(renderer='home.pt')
class ApiViews:
    def __init__(self, request):
        self.request = request

    @view_config(
        route_name='home'
    )
    def home(self):
        return {'name': 'Home View'}

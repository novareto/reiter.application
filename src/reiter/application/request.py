import cgi
import typing
import horseman.parsers
from horseman.http import ContentType
from roughrider.routing.components import RoutingRequest
from reiter.application.registries import NamedComponents


class Request(RoutingRequest):

    __slots__ = (
        '_data'
        '_extracted',
        'app',
        'content_type',
        'environ',
        'method',
        'route',
        'utilities',
    )

    def __init__(self, app, environ, route):
        self._data = {}
        self._extracted = False
        self.app = app
        self.environ = environ
        self.script_name = environ['SCRIPT_NAME']
        self.method = environ['REQUEST_METHOD'].upper()
        self.route = route
        self.utilities = NamedComponents()
        if 'CONTENT_TYPE' in self.environ:
            self.content_type = ContentType.from_http_header(
                self.environ['CONTENT_TYPE'])
        else:
            self.content_type = None

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def extract(self):
        if self._extracted:
            return self.get_data()

        self._extracted = True
        if self.content_type:
            self.set_data(horseman.parsers.parser(
                self.environ['wsgi.input'], self.content_type))

        return self.get_data()

    def route_path(self, name, **params):
        return self.script_name + self.app.routes.url_for(name, **params)

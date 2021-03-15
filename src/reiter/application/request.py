import cgi
import typing
import horseman.parsing
from roughrider.routing.components import RoutingRequest
from reiter.application.registries import NamedComponents


class ContentType(typing.NamedTuple):
    raw: str
    mimetype: str
    options: dict


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
            ct = self.environ['CONTENT_TYPE']
            self.content_type = ContentType(ct, *cgi.parse_header(ct))
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
        if content_type := self.content_type:
            self.set_data(horseman.parsing.parse(
                self.environ['wsgi.input'], content_type.raw))

        return self.get_data()

    def route_path(self, name, **params):
        return self.script_name + self.app.routes.url_for(name, **params)

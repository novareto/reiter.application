import horseman.parsers
import urllib.parse
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

    def application_uri(self):
        server = self.environ['SERVER_NAME']
        scheme = self.environ.get('wsgi.url_scheme', 'http')
        port = self.environ.get('SERVER_PORT', '80')
        if port != '80':
            return f"{scheme}://{server}:{port}{self.script_name}"
        return f"{scheme}://{server}{self.script_name}"

    def uri(self, include_query=True):
        url = self.application_uri()
        path_info = urllib.parse.quote(self.environ.get('PATH_INFO',''))
        if include_query:
            qs = urllib.parse.quote(self.environ.get('QUERY_STRING'))
            if qs:
                return f"{url}{path_info}?{qs}"
        return f"{url}{path_info}"

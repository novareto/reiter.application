from reiter.events.meta import Event


class RouteFound(Event):

    def __init__(self, app, route, environ):
        self.app = app
        self.route = route
        self.environ = environ


class RequestCreated(Event):

    def __init__(self, app, request):
        self.app = app
        self.request = request


class ResponseCreated(Event):

    def __init__(self, app, request, response):
        self.app = app
        self.request = request
        self.response = response

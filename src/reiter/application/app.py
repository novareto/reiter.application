from dataclasses import dataclass, field
from functools import partial, reduce
from omegaconf.dictconfig import DictConfig
from typing import Mapping, Optional, Callable

import horseman.http
import horseman.meta
import horseman.response
from roughrider.routing.route import Routes
from roughrider.events.meta import EventsCenter
from reiter.application import registries


@dataclass
class Blueprint(EventsCenter):

    name: str = None
    config: Mapping = field(default_factory=partial(DictConfig, {}))
    utilities: Mapping = field(default_factory=registries.NamedComponents)
    routes: Routes = field(default_factory=Routes)

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def apply(self, app: 'Blueprint'):
        app.routes += self.routes
        if self.config:
            app.config.update(self.config)
        if self.utilities:
            app.utilities += self.utilities
        if self.subscribers:
            app.subscribers += self.subscribers


@dataclass
class Application(Blueprint, horseman.meta.APINode):

    _caller: Optional[Callable] = None
    middlewares: list = field(default_factory=registries.PriorityList)

    def resolve(self, path, environ):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            self.notify('route_found', self, route, environ)
            request = self.request_factory(self, environ, route)
            self.notify('request_created', self, request)
            response = route.endpoint(request, **route.params)
            self.notify('response_created', self, request, response)
            return response
        return None

    def register_middleware(self, middleware, order):
        self.middlewares.register(middleware, order=order)
        self._caller = reduce(
            lambda x, y: y(x),
            (func for order, func in reversed(self.middlewares)),
            super().__call__
        )

    def __call__(self, environ, start_response):
        environ['app'] = self
        if self._caller is not None:
            return self._caller(environ, start_response)
        return super().__call__(environ, start_response)

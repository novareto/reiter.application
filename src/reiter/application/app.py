from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial, reduce
from typing import Mapping, Optional, Callable

import horseman.meta
import horseman.response
import horseman.http
from roughrider.routing.route import Routes
from omegaconf.dictconfig import DictConfig


@dataclass
class Router(horseman.meta.APINode):

    _caller: Optional[Callable] = default=None

    config: Mapping = field(default_factory=partial(DictConfig, {}))
    connector: Optional[Connector] = None
    middlewares: list = field(default_factory=registries.PriorityList)
    plugins: Mapping = field(default_factory=registries.NamedComponents)
    routes: Routes = field(default_factory=Routes)
    subscribers: dict = field(default_factory=partial(defaultdict, list))

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def notify(self, event_name: str, *args, **kwargs):
        for subscriber in self.subscribers[event_name]:
            if (result := subscriber(*args, **kwargs)):
                return result

    def subscribe(self, event_name: str):
        def wrapper(func):
            self.subscribers[event_name].append(func)
            return func
        return wrapper

    def resolve(self, path, environ):
        route = self.routes.match(
            environ['REQUEST_METHOD'], path)
        if route is not None:
            self.notify('route_found', self, route, environ)
            request = self.request_factory(self, environ, route)
            self.notify('request_created', self, request)
            response = route.endpoint(request, **route.params)
            self.notify('response_created', self, request, response)
            return response
        return None

    def register_middleware(self, middleware, order):
        self._middlewares.register(middleware, order=order)
        self._caller = reduce(
            lambda x, y: y(x),
            (func for order, func in reversed(self._middlewares)),
             super().__call__
        )

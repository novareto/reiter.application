from dataclasses import dataclass, field
from functools import partial
from omegaconf.dictconfig import DictConfig
from typing import Mapping

import horseman.http
import horseman.meta
import horseman.response
from roughrider.routing.route import Routes
from reiter.application.request import Request
from roughrider.events.meta import EventsCenter
from reiter.application import registries
from reiter.application.browser.registries import UIRegistry


@dataclass
class Blueprint(EventsCenter):
    """Application skeleton.
    """
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
    """Barebone application
    """
    request_factory: Request = field(default_factory=Request)

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


@dataclass
class BrowserApplication(Application):
    """Application with browser/UI components.
    """
    ui: UIRegistry = field(default_factory=UIRegistry)

from dataclasses import dataclass, field
from typing import Mapping

import horseman.http
import horseman.meta
import horseman.response
from reiter.events import Subscribers
from reiter.application import events
from reiter.application import registries
from reiter.application.browser.registries import UIRegistry
from reiter.application.request import Request
from roughrider.routing.route import Routes


@dataclass
class Blueprint:
    """Application skeleton.
    """
    name: str = None
    utilities: Mapping = field(default_factory=registries.NamedComponents)
    routes: Routes = field(default_factory=Routes)
    subscribers: Subscribers = field(default_factory=Subscribers)

    def route(self, *args, **kwargs):
        return self.routes.register(*args, **kwargs)

    def notify(self, *args, **kwargs):
        return self.subscribers.notify(*args, **kwargs)

    def apply(self, app: 'Blueprint'):
        app.routes += self.routes
        if self.config:
            app.config.update(self.config)
        if self.utilities:
            app.utilities += self.utilities
        if self.subscribers:
            app.subscribers += self.subscribers


@dataclass
class Application(Blueprint, horseman.meta.Node):
    """Barebone application
    """
    request_factory: Request = field(default=Request)

    def resolve(self, path, environ):
        route = self.routes.match_method(path, environ['REQUEST_METHOD'])
        if route is not None:
            self.notify(events.RouteFound(self, route, environ))
            request = self.request_factory(self, environ, route)
            self.notify(events.RequestCreated(self, request))
            response = route.endpoint(request, **route.params)
            self.notify(events.ResponseCreated(self, request, response))
            return response
        return None


@dataclass
class BrowserApplication(Application):
    """Application with browser/UI components.
    """
    ui: UIRegistry = field(default_factory=UIRegistry)

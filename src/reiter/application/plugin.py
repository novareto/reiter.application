from collections import defaultdict
from dataclasses import dataclass
from typing import Optional
from reiter.application.app import Router
from reiter.application.registries import PriorityList, NamedComponents


@dataclass
class Plugin:

    name: str
    config: Mapping = field(default_factory=dict)
    middlewares: list = field(default_factory=PriorityList)
    plugins: Mapping = field(default_factory=NamedComponents)
    routes: Routes = field(default_factory=NamedComponents)
    subscribers: dict = field(default_factory=partial(defaultdict, list))

    def apply(self, app: Router):
        if self.config is not None:
            app.config.update(self.config)

        if self.middlewares:
            pass

import multidict
import itertools
from typing import (
    Callable, Dict, TypeVar, Tuple, Iterable, Optional, Reversible, Sized)


Component = TypeVar('Component')


class NamedComponents(Dict[str, Component]):

    def __init__(self, items: Optional[Dict[str, Component]] = None):
        if items is not None:
            if not all(isinstance(key, str) for key in items):
                raise TypeError('All keys must be strings.')
            super().__init__(items)

    def register(self, component: Component, name: str):
        self[name] = component

    def component(self, name: str):
        """Component decorator
        """
        def register_component(component: Component) -> Component:
            self.register(component, name)
            return component
        return register_component

    def unregister(self, name: str) -> None:
        del self[name]

    def __add__(self, components: dict):
        return self.__class__({**self, **components})

    def __setitem__(self, name: str, component: Component):
        if not isinstance(name, str):
            raise TypeError('Key must be a string.')
        return super().__setitem__(name, component)


class Subscribers(multidict.MultiDict):

    def __add__(self, subdict: multidict.MultiDict):
        return self.__class__(
            itertools.chain(self.items(), subdict.items()))

    def subscribe(self, name: str):
        def add_subscriber(subscriber: Callable) -> Callable:
            self.add(name, subscriber)
            return subscriber
        return add_subscriber

    def notify(self, name: str, *args, **kwargs):
        if name in self:
            for subscriber in self.getall(name):
                if (result := subscriber(*args, **kwargs)):
                    # Having a result does stop the iteration.
                    return result


PriorityIterable = Iterable[Tuple[int, Component]]


class PriorityList(Reversible, Sized, PriorityIterable):

    __slots__ = ('_components',)

    def __init__(self, components: Optional[PriorityIterable] = None):
        if components is None:
            self._components = []
        else:
            self._components = list(sorted(components))

    def register(self, item: Component, order: int):
        self._components.append((order, item))
        self._components.sort()

    def unregister(self, item: Component, order: int):
        self._components = list(
            filter((order, item).__ne__, self._components)
        )

    def __len__(self):
        return len(self._components)

    def __iter__(self):
        return iter(self._components)

    def __reversed__(self):
        return reversed(self._components)

    def __add__(self, priority_iterable: PriorityIterable):
        if not isinstance(priority_iterable, PriorityList):
            raise TypeError(
                f"unsupported operand type(s) for +: "
                f"'{self.__class__.__name__}' "
                f"and '{priority_iterable.__class__.__name__}'")
        return self.__class__(
            itertools.chain(self._components, priority_iterable))

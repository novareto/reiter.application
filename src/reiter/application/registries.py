import heapq
from collections import abc
from typing import Callable, Tuple, Iterable, Optional


class NamedComponents(dict):

    def register(self, component, name):
        self[name] = component

    def component(self, name):
        """Component decorator
        """
        def register_component(component):
            self.register(component, name)
            return component
        return register_component

    def unregister(self, name):
        del self[name]

    def __add__(self, components: dict):
        return self.__class__({**self, **components})


PriorityIterable = Iterable[Tuple[int, Callable]]


class PriorityList(PriorityIterable, abc.Reversible, abc.Sized):

    __slots__ = ('_components',)

    def __init__(self, components: Optional[PriorityIterable] = None):
        if components is None:
            self._components = []
        else:
            self._components = list(components)
            heapq.heapify(self._components)

    def register(self, item: Callable, order: int):
        heappush(self._components, (order, item))

    def __len__(self):
        return len(self._components)

    def __iter__(self):
        return iter(self._components)

    def __reversed__(self):
        return reversed(self._components)

    def __add__(self, priority_iterable: PriorityIterable):
        assert isinstance(priority_iterable, PriorityIterable)
        components = self._components + list(priority_iterable)
        return self.__class__(components)

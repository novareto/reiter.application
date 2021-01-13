import importlib
import importscan
from pkg_resources import iter_entry_points


def load() -> dict:
    plugins = {}
    for bp in iter_entry_points('reiter.application.blueprints'):
        module = bp.load()
        importscan.scan(module)
        plugin = getattr(module, 'blueprint', None)
        if plugin is None:
            raise RuntimeError(
                f'Plugin {module} has no defined blueprint.'
            )
        plugins[bp.name] = plugin
    return plugins

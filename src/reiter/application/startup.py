import colorlog
import contextlib
import logging
import os


@contextlib.contextmanager
def environment(**environ):
    """Temporarily set the process environment variables.
    """
    old_environ = dict(os.environ)
    os.environ.update(dict(environ))
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def make_logger(name, level=logging.DEBUG) -> logging.Logger:
    logger = colorlog.getLogger(name)
    logger.setLevel(level)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(red)s%(levelname)-8s%(reset)s '
        '%(yellow)s[%(name)s]%(reset)s %(green)s%(message)s'))
    logger.addHandler(handler)
    return logger

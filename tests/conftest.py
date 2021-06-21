import pytest
from frozendict import frozendict
from io import StringIO


@pytest.fixture(scope="session")
def environ():
    return frozendict({
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'SERVER_NAME': 'test_domain.com',
        'SERVER_PORT': '80',
        'HTTP_HOST': 'test_domain.com:80',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'wsgi.url_scheme': 'http',
        'wsgi.version': (1,0),
        'wsgi.run_once': 0,
        'wsgi.multithread': 0,
        'wsgi.multiprocess': 0,
        'wsgi.input': StringIO(""),
        'wsgi.errors': StringIO()
    })

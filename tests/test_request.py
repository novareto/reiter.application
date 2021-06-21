import pytest
from reiter.application.request import Request
from horseman.http import ContentType, HTTPError


def test_method(environ):
    request = Request(None, environ, None)
    assert request.method == 'GET'


def test_utilities(environ):
    from reiter.application.registries import NamedComponents

    request = Request(None, environ, None)
    assert request.utilities == {}
    assert isinstance(request.utilities, NamedComponents)


def test_environ(environ):
    request = Request(None, environ, None)
    assert request.environ is environ


def test_script_name(environ):
    request = Request(None, environ, None)
    assert request.script_name == ""

    environ = {**environ, "SCRIPT_NAME": "/backend"}
    request = Request(None, environ, None)
    assert request.script_name == "/backend"


def test_app_uri(environ):
    request = Request(None, environ, None)
    assert request.application_uri() == 'http://test_domain.com'

    environ = {**environ, "SCRIPT_NAME": "/backend"}
    request = Request(None, environ, None)
    assert request.application_uri() == 'http://test_domain.com/backend'


def test_uri(environ):
    request = Request(None, environ, None)
    assert request.uri() == 'http://test_domain.com/'

    environ = {**environ, "SCRIPT_NAME": "/backend"}
    request = Request(None, environ, None)
    assert request.uri() == 'http://test_domain.com/backend/'

    environ = {**environ, "SCRIPT_NAME": "/backend", "PATH_INFO": "/login"}
    request = Request(None, environ, None)
    assert request.uri() == 'http://test_domain.com/backend/login'

    environ = {
        **environ,
        "SCRIPT_NAME": "/backend",
        "PATH_INFO": "/login",
        "QUERY_STRING": "user=Stéphane"
    }
    request = Request(None, environ, None)
    assert request.uri() == (
        'http://test_domain.com/backend/login?user%3DSt%C3%A9phane')


def test_app_uri(environ):
    request = Request(None, environ, None)
    assert request.application_uri() == 'http://test_domain.com'

    environ = {**environ, "SCRIPT_NAME": "/backend"}
    request = Request(None, environ, None)
    assert request.application_uri() == 'http://test_domain.com/backend'


def test_content_type(environ):
    from io import BytesIO
    from horseman.parsers import Data

    request = Request(None, environ, None)
    assert request.content_type is None
    assert request.get_data() == {}

    environ = {
        **environ,
        "CONTENT_TYPE": "application/json"
    }
    request = Request(None, environ, None)
    assert request.content_type == ContentType(
        mimetype='application/json', options={})
    with pytest.raises(HTTPError) as exc:
        request.extract()
    assert exc.value.body == 'The body of the request is empty.'

    environ = {
        **environ,
        "CONTENT_TYPE": "application/json",
        "wsgi.input": BytesIO(b'''{"a": "b"}''')
    }
    request = Request(None, environ, None)
    assert request.content_type == ContentType(
        mimetype='application/json', options={})
    assert request.extract() == Data(
        form=None,
        files=None,
        json={'a': 'b'}
    )

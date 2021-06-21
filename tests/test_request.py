from reiter.application.request import Request


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

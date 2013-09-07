import cgi
from functools import wraps

# Errors

class UnauthorizedError(Exception):
    pass

class InternalError(Exception):
    pass

class NotFoundError(Exception):
    pass

# Helpers

def errorable(error):
    error_str = b""
    for e in error.args:
        if not isinstance(e, bytes):
            e = e.encode("utf8")
        error_str += b" " + e
    return error_str

def response(func):
    @wraps(func)
    def wrapper(environ, start_response):
        if environ["REQUEST_METHOD"] == "POST":
            if environ.get("wsgi.version", None):
                env = environ.copy()
                env['QUERY_STRING'] = ''
                form = cgi.FieldStorage(
                    fp=env['wsgi.input'],
                    environ=env,
                    keep_blank_values=True
                )
            else:
                form = cgi.FieldStorage()
            environ["rugmi.form"] = form

        try:
            data = func(environ, start_response)
            content_type = "text/html"
            if type(data) is tuple:
                data, content_type = data
            start_response('200 OK', [('Content-Type', content_type)])
        except UnauthorizedError as error:
            start_response('401 Unauthorized',
                    [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Unauthorized, man"
        except InternalError as error:
            start_response('500 Internal Error',
                    [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Error"
        except NotFoundError as error:
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            data = errorable(error) or b"Not Found"
        except Exception as error:
            start_response('500 Internal Error',
                    [('Content-Type', 'text/plain')])
            data = b"Unhandled Error"
            if debug:
                data += b"\n\n"
                data += errorable(error)
        return [data]
    return wrapper

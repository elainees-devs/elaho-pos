"""
Context variable storage for request-specific data.

Used to make the current request and authenticated user
available throughout the application without passing them
through every method.

Uses contextvars.ContextVar instead of threading.local so that
it is safe for both synchronous threads and async task contexts.
"""

from contextvars import ContextVar

_request_var: ContextVar = ContextVar("request")


def set_current_request(request):
    _request_var.set(request)


def get_current_request():
    return _request_var.get(None)


def get_current_user():
    request = get_current_request()

    if request and hasattr(request, "user"):
        return request.user

    return None
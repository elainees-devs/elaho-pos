"""
Thread-local storage for request-specific data.

Used to make the current request and authenticated user
available throughout the application without passing them
through every method.
"""

from threading import local

_thread_locals = local()


def set_current_request(request):
    _thread_locals.request = request


def get_current_request():
    return getattr(_thread_locals, "request", None)


def get_current_user():
    request = get_current_request()

    if request and hasattr(request, "user"):
        return request.user

    return None
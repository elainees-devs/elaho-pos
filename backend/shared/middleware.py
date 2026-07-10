"""
Application middleware.

Responsibilities
----------------
- Store the current request in a context variable.
- Make the authenticated user accessible application-wide.
- Clean up the context variable after each request.

This middleware should not contain business logic.
"""

from .thread_local import set_current_request


class CurrentRequestMiddleware:
    """
    Stores the current request for the duration of a request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        set_current_request(request)

        try:
            response = self.get_response(request)
        finally:
            set_current_request(None)

        return response
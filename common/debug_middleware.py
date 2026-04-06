import sys
import traceback


class DebugExceptionMiddleware:
    """Temporary middleware to print full tracebacks to stderr for 500 errors."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        print(f"\n[DEBUG MIDDLEWARE] Exception on {request.method} {request.path}:", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return None  # let Django handle the response

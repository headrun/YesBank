from django.conf import settings

class APIMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.urlconf = settings.ROOT_URLCONF
        if request.META['HTTP_HOST'].split('.')[0] == 'api':
            request.urlconf = request.urlconf + '.api'
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

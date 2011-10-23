from time import time

from django.conf import settings

from djangosampler.sampler import should_sample, sample

class SamplingMiddleware(object):
    request_start_times = {}
    request_view_calls = {}

    def process_request(self, request):
        self.request_start_times[request] = time()

    def process_response(self, request, response):
        duration = time() - self.request_start_times.pop(request)
        
        view_fallback = {
            'function': request.path,
            'args': [],
            'kwargs': {},
        }
        view_call = self.request_view_calls.pop(request, view_fallback)

        if should_sample(duration):
            sample('request', 
                   view_call['function'], 
                   duration, 
                   [view_call['args'], view_call['kwargs']])

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.request_view_calls[request] = {
            'function': view_func.func_name,
            'args': view_args,
            'kwargs': view_kwargs,
        }
        return None


class Request(object):
    '''Plugin that uses Django's Request signals to provide sampling
    of requests.
    '''

    @staticmethod
    def install():
        settings.MIDDLEWARE_CLASSES = \
            ('djangosampler.plugins.request.SamplingMiddleware', ) + \
            tuple(settings.MIDDLEWARE_CLASSES)

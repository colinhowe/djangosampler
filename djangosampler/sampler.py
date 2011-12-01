from time import time
import json
import random
import traceback

from django.conf import settings
from django.db.models import F
from django.db.utils import DatabaseError
from django.utils.encoding import force_unicode

from models import Query, Sample, Stack

USE_COST = getattr(settings, 'DJANGO_SAMPLER_USE_COST', False)
FREQ = float(getattr(settings, 'DJANGO_SAMPLER_FREQ', 0))
BASE_TIME = float(getattr(settings, 'DJANGO_SAMPLER_BASE_TIME', 0.005))

def _get_tidy_stacktrace():
    """Gets a tidy stacktrace. The tail of the stack is removed to exclude 
    sampler internals. Will return a tuple of the stack printed cleanly and
    a boolean indicating whether the stack contains traces from the sampler
    itself (indicates the sampler being sampled).
    """
    stack = traceback.extract_stack()
    tidy_stack = [] 
    sampler_in_stack = False
    for trace in stack[:-3]:
        if 'djangosampler' in trace[0] and '/sampler.py' in trace[0]:
            sampler_in_stack = True
        
        tidy_stack.append("%s:%s (%s): %s" % trace)

    return "\n".join(tidy_stack), sampler_in_stack

def _calculate_bias(time):
    bias = time / BASE_TIME
    if FREQ * bias > 1:
        bias = 1 / FREQ
    return bias

def _calculate_cost(time):
    if USE_COST:
        bias = _calculate_bias(time)
        cost = time / bias
        return cost
    else:
        return 0.0

def _json_params(params):
    try:
        return json.dumps([force_unicode(x) for x in params])
    except TypeError:
        return ''

def should_sample(time):
    '''Determines if a sample should be taken. The probability of this will
    be multiplied by the time if cost-based sampling is enabled.
    '''
    if USE_COST:
        bias = _calculate_bias(time)
        return random.random() > 1 - FREQ * bias
    else:
        return random.random() < FREQ
 

def sample(query_type, query, time, params):
    '''Main method that records the given query. 
    
    The params argument will be
    recorded alongside individual samples as a JSON object. It is a suitable 
    place to store things like SQL parameters.
    '''
    stack, recursed = _get_tidy_stacktrace()
    if recursed:
        # Don't log the sampler being sampled
        return

    # The same stack may create different queries - so we have to include the
    # query in the stack hash to ensure that it is unique for every query
    stack_hash = hash((tuple(stack), query))

    query_hash = hash((query_type, query))
    try:
        query_model, _ = Query.objects.get_or_create(
                hash=query_hash, defaults={
                    'query_type': query_type, 'query': query
                })
    except DatabaseError:
        # This is likely because the database hasn't been created yet.
        # We can exit here - we don't want to cause the world to break
        return

    try:
        stack_model, _ = Stack.objects.get_or_create(
                hash=stack_hash, 
                defaults={'stack': stack, 'query': query_model})
    except DatabaseError:
        # This is likely because the database hasn't been created yet.
        # We can exit here - we don't want to cause the world to break
        return

    cost = _calculate_cost(time)
    params = _json_params(params)

    try:
        Sample.objects.create(
                query=query, params=params, duration=time, cost=cost,
                stack=stack_model)
    except DatabaseError:
        # This is likely because the database hasn't been created yet.
        # We can exit here - we don't want to cause the world to break
        return

    # Update the stack total times
    Stack.objects.filter(hash=stack_hash).update(
            total_duration=F('total_duration') + time,
            total_cost=F('total_cost') + cost,
            count=F('count') + 1)

    # Update the query total times
    Query.objects.filter(hash=query_hash).update(
            total_duration=F('total_duration') + time,
            total_cost=F('total_cost') + cost,
            count=F('count') + 1)

class sampling:
    def __init__(self, sample_type, sample_key, params=()):
        self.sample_type = sample_type
        self.sample_key = sample_key
        self.params = params

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, type, value, traceback):
        end_time = time()
        duration = end_time - self.start_time

        if should_sample(duration):
            sample(self.sample_type, self.sample_key, duration, self.params)

        return False

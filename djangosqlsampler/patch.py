import django
import json
import os
import random
import traceback

from django.conf import settings
from django.db.models import F
from django.db.utils import DatabaseError
from django.utils.encoding import force_unicode
from models import Query, Sample, Stack
from time import time

SQL_SAMPLE_COST = getattr(settings, 'SQL_SAMPLE_COST', False)
SQL_SAMPLE_FREQ = float(getattr(settings, 'SQL_SAMPLE_FREQ', 0))

def get_tidy_stacktrace():
    """Gets a tidy stacktrace. The tail of the stack is removed to exclude 
    sampler internals. Will return a tuple of the stack printed cleanly and
    a boolean indicating whether the stack contains traces from the sampler
    itself (indicates the sampler being sampled).
    """
    stack = traceback.extract_stack()
    tidy_stack = [] 
    sampler_in_stack = False
    for trace in stack[:-3]:
        if 'djangosqlsampler' in trace[0]:
            sampler_in_stack = True
        
        tidy_stack.append("%s:%s (%s): %s" % trace)

    return "\n".join(tidy_stack), sampler_in_stack


class SamplingCursorWrapper(object):
    """A cursor wrapper that will sample a % of SQL queries.
    """
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def _should_sample(self, time):
        if SQL_SAMPLE_COST:
            return time * random.random() > 1 - SQL_SAMPLE_FREQ
        else:
            return random.random() < SQL_SAMPLE_FREQ

    def _calculate_cost(self, time):
        if SQL_SAMPLE_COST:
            cost = max(1.0, time * SQL_SAMPLE_FREQ) 
            cost /= SQL_SAMPLE_FREQ
            return cost
        else:
            return 0.0

    def _json_params(self, params):
        try:
            return json.dumps([force_unicode(x) for x in params])
        except TypeError:
            return ''

    def log_sql(self, sql, time, params):
        if not self._should_sample(time):
            return

        stack, recursed = get_tidy_stacktrace()
        if recursed:
            # Don't log the sampler being sampled
            return
        # The same stack may create different SQL - so we have to include the
        # SQL in the stack hash to ensure that it is unique for every query
        stack_hash = hash((tuple(stack), sql))

        sql_hash = hash(sql)
        try:
            query_model, _ = Query.objects.get_or_create(
                    hash=sql_hash, defaults={'sql': sql})
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

        cost = self._calculate_cost(time)
        params = self._json_params(params)

        try:
            sample_model = Sample.objects.create(
                    sql=sql, params=params, duration=time, cost=cost,
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
        Query.objects.filter(hash=sql_hash).update(
                total_duration=F('total_duration') + time,
                total_cost=F('total_cost') + cost,
                count=F('count') + 1)

    def execute(self, sql, params=()):
        start = time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time()
            self.log_sql(sql, stop - start, params)

    def executemany(self, sql, param_list):
        start = time()
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            stop = time()
            self.log_sql(sql, stop - start, param_list)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

import django.db.backends
old_cursor = django.db.backends.BaseDatabaseWrapper.cursor

def get_cursor(self):
    cursor = old_cursor(self)
    return SamplingCursorWrapper(cursor, self)

django.db.backends.BaseDatabaseWrapper.cursor = get_cursor

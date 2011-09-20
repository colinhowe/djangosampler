import functools
from time import time

from djangosampler.sampler import should_sample, sample

import pymongo

class Mongo(object):
    '''Plugin that patches pyMongo to sample queries.
    '''
    @staticmethod
    def parameterise_dict(d):
        new_d = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_d[k] = Mongo.parameterise_dict(v)
            else:
                new_d[k] = '*'
        return new_d

    @staticmethod
    def get_insert_query(collection, *args, **kwargs):
        return '%s.insert(...)' % collection.name

    @staticmethod
    def get_update_query(collection, spec, document, upsert=False, *args, **kwargs):
        safe_spec = Mongo.parameterise_dict(spec)
        update_method = upsert and 'upsert' or 'update'
        return '%s.%s(%s)' % (collection.name, update_method, repr(safe_spec))

    @staticmethod
    def get_remove_query(collection, spec_or_id, safe=False, **kwargs):
        if isinstance(spec_or_id, dict):
            safe_spec = Mongo.parameterise_dict(spec_or_id)
        else:
            safe_spec = { '_id': spec_or_id }

        return '%s.remove(%s)' % (collection.name, repr(safe_spec))
    
    @staticmethod
    def privar(cursor, name):
        return getattr(cursor, '_Cursor__{0}'.format(name))

    @staticmethod
    def should_sample_refresh(cursor):
        return Mongo.privar(cursor, 'id') is not None

    @staticmethod
    def get_refresh_query(cursor):
        query_son = Mongo.privar(cursor, 'query_spec')()

        # In db_name.collection_name format
        collection_name = Mongo.privar(cursor, 'collection').full_name 
        collection_name = collection_name.split('.')[1]

        query_spec = {}

        ordering = None
        if collection_name == '$cmd':
            command = 'command'
            # Handle count as a special case
            if 'count' in query_son:
                # Information is in a different format to a standard query
                collection_name = query_son['count']
                command = 'count'
                query_spec['query'] = query_son['query']
        else:
            # Normal Query
            command = 'query'
            query_spec['query'] = query_son['$query']

            def fmt(field, direction):
                return '{0}{1}'.format({-1: '-', 1: '+'}[direction], field)

            if '$orderby' in query_son:
                ordering = ', '.join(fmt(f, d) 
                        for f, d in query_son['$orderby'].items())


        query_spec = Mongo.parameterise_dict(query_spec)
        if ordering:
            query_spec['ordering'] = ordering
        return "%s.%s(%s)" % (collection_name, command, repr(query_spec))

    @staticmethod
    def make_wrapper(name, method):
        sampling_method = getattr(Mongo, 'get_%s_query' % name)
        should_sample_method = getattr(Mongo, 'should_sample_%s' % name, 
                lambda *args, **kwargs: True)
        def sampler(*args, **kwargs):
            start = time()
            try:
                should_sample_query = should_sample_method(*args, **kwargs)
                return method(*args, **kwargs)
            finally:
                stop = time()
                if should_sample_query and should_sample(stop - start):
                    query = sampling_method(*args, **kwargs)
                    if query:
                        sample('mongo', query, stop - start, [args, kwargs])

        return sampler



    @staticmethod
    def install():
        wrapped_methods = {
            'insert': pymongo.collection.Collection.insert,
            'update': pymongo.collection.Collection.update,
            'remove': pymongo.collection.Collection.remove,
            'refresh': pymongo.cursor.Cursor._refresh,
        }

        for name, method in wrapped_methods.items():
            setattr(
                method.im_class, 
                method.im_func.func_name, 
                Mongo.make_wrapper(name, method))
        

class SamplingCursorWrapper(object):
    """A cursor wrapper that will sample a % of SQL queries.
    """
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def log_sql(self, sql, time, params):
        if not should_sample(time):
            return
        sample('sql', sql, time, params)

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


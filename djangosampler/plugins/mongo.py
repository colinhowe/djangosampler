import time

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
        return '%s.insert(...)' % collection.name, 'mongo'

    @staticmethod
    def get_update_query(collection, spec, document, upsert=False, *args, **kwargs):
        safe_spec = Mongo.parameterise_dict(spec)
        update_method = upsert and 'upsert' or 'update'
        query = '%s.%s(%s)' % (collection.name, update_method, repr(safe_spec))
        return query, 'mongo'

    @staticmethod
    def get_remove_query(collection, spec_or_id, safe=False, **kwargs):
        if isinstance(spec_or_id, dict):
            safe_spec = Mongo.parameterise_dict(spec_or_id)
        else:
            safe_spec = { '_id': spec_or_id }

        return '%s.remove(%s)' % (collection.name, repr(safe_spec)), 'mongo'
    
    @staticmethod
    def privar(cursor, name):
        return getattr(cursor, '_Cursor__{0}'.format(name))

    @staticmethod
    def pre_refresh(cursor):
        cursor._is_getmore = Mongo.privar(cursor, 'id') is not None
        cursor._slave_okay = (
            Mongo.privar(cursor, 'slave_okay') 
            or not Mongo.privar(cursor, 'must_use_master'))

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
            if cursor._is_getmore:
                command = 'cursor_more'
            else:
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
        query_type = 'mongo'
        if cursor._slave_okay:
            query_type = 'mongo slave'
        print 'Query type: %s' % query_type
        query = "%s.%s(%s)" % (collection_name, command, repr(query_spec))
        return query, query_type

    @staticmethod
    def make_wrapper(name, method):
        sampling_method = getattr(Mongo, 'get_%s_query' % name)
        pre_invoke = getattr(Mongo, 'pre_%s' % name, None)
        def sampler(*args, **kwargs):
            start = time.time()
            try:
                if pre_invoke:
                    pre_invoke(*args, **kwargs)
                return method(*args, **kwargs)
            finally:
                stop = time.time()
                if should_sample(stop - start):
                    query, query_type = sampling_method(*args, **kwargs)
                    if query:
                        sample(query_type, query, stop - start, [args, kwargs])

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

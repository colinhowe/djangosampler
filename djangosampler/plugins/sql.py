import json
from time import time

from django.db import connection

from djangosampler.sampler import should_sample, sample
from djangosampler.models import Sample

class Sql(object):
    '''Plugin that patches Django's cursors to use a sampling cursor.
    '''

    @staticmethod
    def install():
        from django.db.backends.base.base import BaseDatabaseWrapper
        old_cursor = BaseDatabaseWrapper.cursor

        def cursor(self):
            new_cursor = old_cursor(self)
            return SamplingCursorWrapper(new_cursor, self)

        setattr(BaseDatabaseWrapper.cursor.im_class, 'cursor', cursor)

    @staticmethod
    def get_query_view_addons():
        return { 'sql': Sql.query_view_addon }

    @staticmethod
    def query_view_addon(query, stacks):
        sample_query = Sample.objects.filter(stack=stacks[0])[0]
        # Get an explain plain
        cursor = None
        explain = 'Unavailable'
        try:
            cursor = connection.cursor()
            raw_query = sample_query.query
            params = json.loads(sample_query.params)
            cursor.execute('EXPLAIN %s' % raw_query, params)
            explain = 'EXPLAIN %s\n\n' % (raw_query % tuple(params))
            row = cursor.fetchone()
            explain += "Select type:   %s\n" % row[1]
            explain += "Table:         %s\n" % row[2]
            explain += "Type:          %s\n" % row[3]
            explain += "Possible keys: %s\n" % row[4]
            explain += "Key:           %s\n" % row[5]
            explain += "Key length:    %s\n" % row[6]
            explain += "Ref:           %s\n" % row[7]
            explain += "Rows:          %s\n" % row[8]
            explain += "Extra:         %s\n" % row[9]

        except Exception:
            pass
        finally:
            if cursor:
                cursor.close()

        return """
            <h3>Example Explain</h3>
            <pre>%s</pre>
        """ % explain


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

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

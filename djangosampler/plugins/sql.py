from time import time

from djangosampler.sampler import should_sample, sample

class Sql(object):
    '''Plugin that patches Django's cursors to use a sampling cursor.
    '''

    @staticmethod
    def install():
        import django.db.backends
        old_cursor = django.db.backends.BaseDatabaseWrapper.cursor

        def get_cursor(self):
            cursor = old_cursor(self)
            return SamplingCursorWrapper(cursor, self)

        django.db.backends.BaseDatabaseWrapper.cursor = get_cursor 

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


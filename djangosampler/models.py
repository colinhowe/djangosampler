from datetime import datetime

from django.db import models


class Query(models.Model):
    """
    A query. This is the highest level of grouping.
    """
    hash = models.CharField(primary_key=True, max_length=32)
    query = models.TextField()
    total_duration = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    query_type = models.CharField(db_index=True, max_length=32)
    created_dt = models.DateTimeField(
            default=datetime.now, editable=False, db_index=True)

    class Meta:
        verbose_name_plural = 'queries'

    def __unicode__(self):
        return self.hash

    def get_hash_for_date(self, hash_date):
        '''
        Gets a hash for the same query but on a different date.
        '''
        return hash((hash_date, self.query_type, self.query))

class Stack(models.Model):
    """
    A stack for a set of queries.
    """
    hash = models.CharField(primary_key=True, max_length=32)
    stack = models.TextField()
    total_duration = models.FloatField(default=0)
    total_cost = models.FloatField(default=0)
    count = models.IntegerField(default=0)
    query = models.ForeignKey('Query')
    created_dt = models.DateTimeField(default=datetime.now, editable=False)

    def last_stack_line(self):
        return self.stack.split('\n')[-1]

    def __unicode__(self):
        return self.hash


class Sample(models.Model):
    """
    A sampled query.
    """
    query = models.TextField()
    duration = models.FloatField()
    cost = models.FloatField()
    stack = models.ForeignKey('Stack')
    params = models.TextField()
    created_dt = models.DateTimeField(default=datetime.now, editable=False)

    @property
    def duration_ms(self):
        return self.duration * 1000.0

    def __unicode__(self):
        return unicode(self.created_dt)


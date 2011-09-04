from django.db import models

class Stack(models.Model):
    """A stack for a set of queries.
    """
    hash = models.CharField(primary_key=True, max_length=32)
    stack = models.TextField()
    total_duration = models.FloatField(default=0, db_index=True)
    total_cost = models.FloatField(default=0, db_index=True)
    count = models.IntegerField(default=0, db_index=True)

    def last_stack_line(self):
        return self.stack.split('\n')[-1]

class Query(models.Model):
    """A sampled SQL query.
    """
    sql = models.TextField()
    duration = models.FloatField()
    cost = models.FloatField()
    stack = models.ForeignKey('Stack')
    params = models.TextField()

    @property
    def duration_ms(self):
        return self.duration * 1000.0

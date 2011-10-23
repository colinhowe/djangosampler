from time import time

from celery.signals import task_prerun, task_postrun

from djangosampler.sampler import should_sample, sample

task_start_times = {}

def task_prerun_handler(task_id, task, args, kwargs, **kwds):
    task_start_times[task_id] = time()

def task_postrun_handler(task_id, task, args, kwargs, retval, **kwds):
    duration = time() - task_start_times[task_id]
    del task_start_times[task_id]

    if not should_sample(duration):
        return

    sample('celery', str(task), duration, [args, kwargs])

class Celery(object):
    '''Plugin that hooks into Celery's signals to provide sampling of task
    duration.
    '''

    @staticmethod
    def install():
        task_prerun.connect(task_prerun_handler)
        task_postrun.connect(task_postrun_handler)


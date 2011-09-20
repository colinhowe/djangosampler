import json
from math import ceil

from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Query, Sample, Stack

PAGE_SIZE = 20

def superuser_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('Forbidden')
    return wrapped_view

@superuser_required
def queries(request, offset=0, sort='total_duration'):
    start_offset = int(offset)
    total_queries = Query.objects.count()
    queries = Query.objects.filter(query_type='mongo').order_by(sort)
    queries = queries.reverse()
    queries = queries[start_offset:start_offset+PAGE_SIZE]
    queries = list(queries)
    end_offset = start_offset + len(queries)

    for query in queries:
        query.url = reverse('query', kwargs={'query_hash': query.hash})

    current_page = 1 + start_offset / PAGE_SIZE
    max_pages = int(ceil(total_queries / float(PAGE_SIZE)))
    pages = xrange(max(1, current_page - 5), 1 + min(max_pages, current_page + 5))

    pages = list([{ 
            'number': page, 
            'url': reverse('queries', kwargs={'offset': PAGE_SIZE * (page - 1), 'sort': sort})
        }
        for page in pages
    ])

    def get_sort_url(field):
        if field == sort:
            field = '-%s' % field
        return reverse('queries', kwargs={'offset': 0, 'sort': field})

    by_count_url = get_sort_url('count')
    by_duration_url = get_sort_url('total_duration')
    by_cost_url = get_sort_url('total_cost')

    return render_to_response('djangosampler/queries.html', 
            locals(),
            context_instance=RequestContext(request))

@superuser_required
def query(request, query_hash):
    query = Query.objects.get(hash=query_hash)

    stacks = Stack.objects.filter(query=query)
    stacks = stacks.order_by('-total_cost')
    stacks = list(stacks)

    sample = Sample.objects.filter(stack=stacks[0])[0]

    # Get an explain plain
    cursor = None
    explain = 'Unavailable'
    try:
        cursor = connection.cursor()
        raw_query = sample.query
        params = json.loads(sample.params)
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

    queries_url = reverse('queries',
            kwargs={'sort': 'total_duration', 'offset': 0})

    return render_to_response('djangosampler/query.html', 
            locals(),
            context_instance=RequestContext(request))

@superuser_required
def index(request):
    return HttpResponseRedirect(reverse('queries',
        kwargs={'sort': 'total_duration', 'offset': 0}))

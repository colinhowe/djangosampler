import json
from math import ceil

from django.core.urlresolvers import reverse
from django.db import connection
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Query, Sample, Stack
from plugins import get_view_addons

PAGE_SIZE = 20

def superuser_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('Forbidden')
    return wrapped_view

@superuser_required
def queries(request, query_type, offset=0, sort='total_duration'):
    start_offset = int(offset)
    total_queries = Query.objects.filter(query_type=query_type).count()
    queries = Query.objects.filter(query_type=query_type).order_by(sort)
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
            'url': reverse('queries', kwargs={
                'query_type': query_type,
                'offset': PAGE_SIZE * (page - 1), 
                'sort': sort
            })
        }
        for page in pages
    ])

    def get_sort_url(field):
        if field == sort:
            field = '-%s' % field
        return reverse('queries', kwargs={
            'query_type': query_type,
            'offset': 0, 
            'sort': field
        })

    by_count_url = get_sort_url('count')
    by_duration_url = get_sort_url('total_duration')
    by_cost_url = get_sort_url('total_cost')

    query_types = _get_query_types()

    return render_to_response('djangosampler/queries.html', 
            {
                'by_count_url': by_count_url,
                'by_duration_url': by_duration_url,
                'by_cost_url': by_cost_url,
                'query_types': query_types,
                'start_offset': start_offset,
                'end_offset': end_offset,
                'total_queries': total_queries,
                'pages': pages,
                'current_page': current_page,
                'queries': queries,
            },
            context_instance=RequestContext(request))

@superuser_required
def query(request, query_hash):
    query = Query.objects.get(hash=query_hash)

    stacks = Stack.objects.filter(query=query)
    stacks = stacks.order_by('-total_cost')
    stacks = list(stacks)

    sample = Sample.objects.filter(stack=stacks[0])[0]

    extra = ""
    for addon in get_view_addons(query.query_type):
        extra += addon(query, stacks)

    query_types = _get_query_types()

    return render_to_response('djangosampler/query.html', 
            locals(),
            context_instance=RequestContext(request))

@superuser_required
def index(request):
    query_type = _get_query_types()[0]['name']
    return HttpResponseRedirect(reverse('queries',
        kwargs={
            'query_type': query_type, 
            'sort': 'total_duration', 
            'offset': 0
    }))

def _get_query_types():
    query_type_names = Query.objects.values_list('query_type', flat=True).distinct()
    query_objs = []
    for query_type in query_type_names:
        query_obj = {}
        query_obj['name'] = query_type
        query_obj['friendly_name'] = query_type.capitalize()
        query_obj['url'] = reverse('queries',
            kwargs={
                'query_type': query_type,
                'sort': 'total_duration', 
                'offset': 0
        })
        query_objs.append(query_obj)
    return query_objs


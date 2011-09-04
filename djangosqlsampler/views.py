from math import ceil

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Stack, Query

PAGE_SIZE = 20

def superuser_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('Forbidden')
    return wrapped_view

@superuser_required
def stacks(request, offset=0, sort='total_duration'):
    start_offset = int(offset)
    total_stacks = Stack.objects.count()
    stacks = Stack.objects.order_by(sort)
    stacks = stacks.reverse()
    stacks = stacks[start_offset:start_offset+PAGE_SIZE]
    stacks = list(stacks)
    end_offset = start_offset + len(stacks)

    for stack in stacks:
        stack.url = reverse('stack', kwargs={'stack_hash': stack.hash})

    current_page = 1 + start_offset / PAGE_SIZE
    max_pages = int(ceil(total_stacks / float(PAGE_SIZE)))
    pages = xrange(max(1, current_page - 5), 1 + min(max_pages, current_page + 5))

    pages = list([{ 
            'number': page, 
            'url': reverse('stacks', kwargs={'offset': PAGE_SIZE * (page - 1), 'sort': sort})
        }
        for page in pages
    ])

    def get_sort_url(field):
        if field == sort:
            field = '-%s' % field
        return reverse('stacks', kwargs={'offset': 0, 'sort': field})

    by_count_url = get_sort_url('count')
    by_duration_url = get_sort_url('total_duration')
    by_cost_url = get_sort_url('total_cost')

    return render_to_response('djangosqlsampler/stacks.html', 
            locals(),
            context_instance=RequestContext(request))

@superuser_required
def stack(request, stack_hash):
    stack = Stack.objects.get(hash=stack_hash)

    queries = Query.objects.filter(stack=stack)
    queries = queries.order_by('-id')
    queries = queries[:10]
    queries = list(queries)

    example_query = queries[0].sql

    stacks_url = reverse('stacks',
            kwargs={'sort': 'total_duration', 'offset': 0})

    return render_to_response('djangosqlsampler/stack.html', 
            locals(),
            context_instance=RequestContext(request))

@superuser_required
def query(request, query_id):
    pass

@superuser_required
def index(request):
    return HttpResponseRedirect(reverse('stacks',
        kwargs={'sort': 'total_duration', 'offset': 0}))

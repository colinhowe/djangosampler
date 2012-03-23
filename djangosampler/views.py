from datetime import datetime, timedelta
from math import ceil

from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Query, Sample, Stack
from plugins import get_view_addons

PAGE_SIZE = 20


@staff_member_required
def queries(request, query_type, date_string, offset=0, sort='total_duration'):
    start_date = datetime.strptime(date_string, '%Y-%m-%d') 
    end_date = start_date + timedelta(days=1)

    start_offset = int(offset)
    query_qs = Query.objects.filter(query_type=query_type,
            created_dt__gte=start_date, created_dt__lt=end_date)

    total_queries = query_qs.count()
    queries = query_qs.order_by(sort)
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
                'date_string': date_string,
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
            'date_string': date_string,
            'query_type': query_type,
            'offset': 0, 
            'sort': field
        })

    by_count_url = get_sort_url('count')
    by_duration_url = get_sort_url('total_duration')
    by_cost_url = get_sort_url('total_cost')

    query_types = _get_query_types(date_string)
    date_links = _get_date_links(start_date, query_type)

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
                'date_links': date_links,
                'current_date': date_string,
                'current_query_type': query_type,
            },
            context_instance=RequestContext(request))

@staff_member_required
def query(request, query_hash):
    query = Query.objects.get(hash=query_hash)

    stacks = Stack.objects.filter(query=query)
    stacks = stacks.order_by('-total_cost')
    stacks = list(stacks)

    sample = Sample.objects.filter(stack=stacks[0])[0]

    extra = ""
    for addon in get_view_addons(query.query_type):
        extra += addon(query, stacks)

    recent_queries = []
    start_date = query.created_dt.date()
    for day in xrange(-7, 7):
        recent_date = start_date + timedelta(days=day)
        recent_query_hash = query.get_hash_for_date(recent_date)
        try:
            recent_query = Query.objects.get(hash=recent_query_hash)
        except Query.DoesNotExist:
            recent_query = None
        recent_queries.append((recent_date, recent_query))


    date_string = query.created_dt.strftime('%Y-%m-%d')
    back_link = reverse('queries',
        kwargs={
            'date_string': date_string,
            'query_type': query.query_type, 
            'sort': 'total_duration', 
            'offset': 0
    })

    return render_to_response('djangosampler/query.html', 
            locals(),
            context_instance=RequestContext(request))

@staff_member_required
def index(request):
    current_date = datetime.now().strftime('%Y-%m-%d')
    query_types = _get_query_types(current_date)
    # don't fail if this is the first time things have been run
    query_type = query_types[0]['name'] if query_types else None
    return HttpResponseRedirect(reverse('queries',
        kwargs={
            'date_string': current_date,
            'query_type': query_type, 
            'sort': 'total_duration', 
            'offset': 0
    }))

def _get_query_types(date_string):

    query_type_names = Query.objects.values_list('query_type', flat=True).distinct()
    query_objs = []
    for query_type in query_type_names:
        query_obj = {}
        query_obj['name'] = query_type
        query_obj['friendly_name'] = query_type.capitalize()
        query_obj['url'] = reverse('queries',
            kwargs={
                'date_string': date_string,
                'query_type': query_type,
                'sort': 'total_duration', 
                'offset': 0
        })
        query_objs.append(query_obj)
    return query_objs


def _get_date_links(current_date, query_type):
    # Want full week before and after the current date
    date_links = []
    for day in xrange(-7, 8):
        date_value = current_date + timedelta(days=day)
        date_link = {}
        date_link['friendly_name'] = date_value.strftime('%Y-%m-%d')
        date_link['url'] = reverse('queries',
            kwargs={
                'date_string': date_link['friendly_name'],
                'query_type': query_type,
                'sort': 'total_duration', 
                'offset': 0
        })
        date_links.append(date_link)

    return date_links



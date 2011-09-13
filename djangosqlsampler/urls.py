from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^queries/(?P<sort>(-|\w)+)/(?P<offset>\d+)/$', views.queries, name='queries'),
    url(r'^queries/by_duration/(?P<offset>\d+)/$', views.queries, name='queries'),
    url(r'^queries/by_cost/(?P<offset>\d+)/$', views.queries, name='queries'),
    url(r'^query/(?P<query_hash>[-0-9]+)/$', views.query, name='query'),

    url(r'^$', views.index, name='index'),
)

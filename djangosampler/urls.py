from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^queries/(?P<query_type>[\w ]+)/(?P<date_string>[-\w\d]+)/(?P<sort>(-|\w)+)/(?P<offset>\d+)/$', views.queries, name='queries'),
    url(r'^query/(?P<query_hash>[-0-9]+)/$', views.query, name='query'),

    url(r'^$', views.index, name='index'),
)

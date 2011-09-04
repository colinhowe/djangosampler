from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^stacks/(?P<sort>(-|\w)+)/(?P<offset>\d+)/$', views.stacks, name='stacks'),
    url(r'^stacks/by_duration/(?P<offset>\d+)/$', views.stacks, name='stacks'),
    url(r'^stacks/by_cost/(?P<offset>\d+)/$', views.stacks, name='stacks'),
    url(r'^stack/(?P<stack_hash>[-0-9]+)/$', views.stack, name='stack'),

    url(r'^$', views.index, name='index'),
)

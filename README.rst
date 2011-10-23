==============
Django Sampler
==============

Author: Colin Howe (@colinhowe)

License: Apache 2.0

About
=====

Django Sampler allows you to sample a percentage of your queries (SQL, Mongo,
etc) and view the ones that are taking up the most time. The queries are grouped
together by where they originated from in your code.

Installation
============

Install::

    python setup.py install

Configure:
 * Add djangosampler to your INSTALLED_APPS
 * Add the tables (manage.py syncdb or manage.py migrate if you use South)
 * Add the views::

    urlpatterns += patterns('',
        (r'^sampler/', include('djangosampler.urls')),
    )

 * Set DJANGO_SAMPLER_FREQ to a value other than 0
 * Set DJANGO_SAMPLER_PLUGINS to a list of plugins. For just sampling SQL a 
   sensible default is::
    
    DJANGO_SAMPLER_PLUGINS = (
        'djangosampler.plugins.sql.Sql',
        # Plugins are applied in the same order as this list
    )

   There are several plugins available and it is worthwhile reading through
   them to get the most use out of this tool.


Viewing Results
===============

After letting the sampler run for a while you will be able to view queries
(grouped by their origin) at the URL you configured.

Configuration
=============

DJANGO_SAMPLER_PLUGINS
~~~~~~~~~~~~~~~~~~~~~~

Django Sampler has a plugin architecture to allow you to control how
much data you want to be collected.

In your settings.py add the following::

    DJANGO_SAMPLER_PLUGINS = (
        'djangosampler.plugins.sql.Sql',
        # Plugins are applied in the same order as this list
    )

The example above will add the SQL plugin.

Available plugins and their settings are described in the Plugins section below.

DJANGO_SAMPLER_FREQ
~~~~~~~~~~~~~~~~~~~

DJANGO_SAMPLER_FREQ configures the percentage of queries that will be recorded. 
It should be between 0.0 and 1.0.

If this is not set then no plugins will be installed and your code will run as 
normal.

DJANGO_SAMPLER_USE_COST
~~~~~~~~~~~~~~~~~~~~~~~

DJANGO_SAMPLER_USE_COST will enable cost-based sampling. This causes queries 
that run for a long time to be sampled more often than short queries. 

The chance that a query is sampled is multiplied by the total time the query
takes. If a query takes 2 seconds then it will be twice as likely to be sampled
as a query that takes 1 second.

The cost for a query is adjusted to account for this as follows::

    cost = max(1.0, time * DJANGO_SAMPLER_FREQ) / DJANGO_SAMPLER_FREQ

Plugins
=======

A list of available plugins follows. You can write your own plugin and this is 
described in the section 'Writing Your Own Plugins'.

Django SQL
~~~~~~~~~~

Plugin class: djangosampler.plugins.sql.Sql

The SQL sampler plugin will sample a percentage of SQL queries that occur in
your application. The samples will be grouped by query and stack traces will be
recorded to find where the queries are originating.

Django Requests
~~~~~~~~~~~~~~~

Plugin class: djangosampler.plugins.request.Request

The request plugin installs a Middleware that will sample the time taken by
requests.

Celery
~~~~~~

Plugin class: djangosampler.plugins.celery_task.Celery

The Celery plugin uses Celery's signals to sample the time taken to execute
tasks.

MongoDB
~~~~~~~

Plugin class: djangosampler.plugins.mongo.Mongo

The MongoDB plugin will sample a percentage of Mongo commands (queries,
inserts, etc) that occur in your application. The samples will be grouped by
command and stack traces will be recorded to find where the queries are 
originating.


Writing Your Own Plugins
========================

TODO. For now, look in the plugins folder and copy :)

Feedback
========

Feedback is always welcome! Github or twitter (@colinhowe) are the best places
to reach me.


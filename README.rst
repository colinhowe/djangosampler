==================
Django SQL Sampler
==================

Author: Colin Howe (@colinhowe)

License: Apache 2.0

About
=====

Django SQL Sampler allows you to sample a percentage of your SQL queries and
view the ones that are taking up the most time. The queries are grouped
together by where they originated from in your code.

Installation
============

Install::

    python setup.py install

Configure:
 * Add djangosqlsampler to your INSTALLED_APPS
 * Add the tables (manage.py syncdb or manage.py migrate if you use South)
 * Add the views::

    urlpatterns += patterns('',
        (r'^sql-sampler/', include('djangosqlsampler.urls')),
    )
 * Configure the set of plugins that you want - the order is important for any
   plugins that apply tags to querys (see Plugins section below)


Plugins
=======

Django SQL Sampler has a plugin architecture to allow you to control how
much data you want to be collected.

In your settings.py add the following::

    DJANGO_SAMPLER_PLUGINS = (
        'sql',
        # Plugins are applied in the same order as this list
    )

The example above will add the SQL plugin.

Available plugins and their settings are described below.

SQL Sampler
-----------

The SQL sampler plugin will sample a percentage of SQL queries that occur in
your application. The samples will be grouped by query and stack traces will be
recorded to find where the queries are originating.

SQL_SAMPLE_FREQ
~~~~~~~~~~~~~~~

SQL_SAMPLE_FREQ configures the percentage of queries that will be recorded. It
should be between 0.0 and 1.0.

If this is not set then the patched cursor will not be installed and your code 
will run as normal.

SQL_SAMPLE_COST
~~~~~~~~~~~~~~~

SQL_SAMPLE_COST will enable cost-based sampling. This causes queries that run
for a long time to be sampled more often than short queries. 

The chance that a query is sampled is multiplied by the total time the query
takes. If a query takes 2 seconds then it will be twice as likely to be sampled
as a query that takes 1 second.

The cost for a query is adjusted to account for this as follows::

    cost = max(1.0, time * SQL_SAMPLE_FREQ) / SQL_SAMPLE_FREQ

Viewing Results
===============

After letting the sampler run for a while you will be able to view queries
(grouped by their origin) at the URL you configured.


Feedback
========

Feedback is always welcome! Github or twitter (@colinhowe) are the best places
to reach me.

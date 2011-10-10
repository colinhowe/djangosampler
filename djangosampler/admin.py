from django.contrib import admin

# from lazy_paginator.paginator import LazyPaginator

from .models import Query, Stack, Sample


class QueryAdmin(admin.ModelAdmin):
    list_display = ('hash', 'cre',)
    list_filter = ('cre',)
    readonly_fields=('cre',)


class StackAdmin(admin.ModelAdmin):
    list_display = ('hash', 'cre',)
    list_filter = ('cre',)
    readonly_fields=('cre',)


class SampleAdmin(admin.ModelAdmin):
    list_display = ('cre',)
    list_filter = ('cre',)
    readonly_fields=('cre',)

    
admin.site.register(Query, QueryAdmin)
admin.site.register(Stack, StackAdmin)
admin.site.register(Sample, SampleAdmin)



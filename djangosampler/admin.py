from django.contrib import admin

# from lazy_paginator.paginator import LazyPaginator

from .models import Query, Stack, Sample


class QueryAdmin(admin.ModelAdmin):
    list_display = ('hash', 'created_dt',)
    list_filter = ('created_dt',)
    readonly_fields=('created_dt',)


class StackAdmin(admin.ModelAdmin):
    list_display = ('hash', 'created_dt',)
    list_filter = ('created_dt',)
    readonly_fields=('created_dt',)


class SampleAdmin(admin.ModelAdmin):
    list_display = ('created_dt',)
    list_filter = ('created_dt',)
    readonly_fields=('created_dt',)

    
admin.site.register(Query, QueryAdmin)
admin.site.register(Stack, StackAdmin)
admin.site.register(Sample, SampleAdmin)



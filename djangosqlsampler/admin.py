from django import forms
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from models import Stack, Query

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        if hasattr(self, 'initial'):
            value = self.initial
        return mark_safe("<pre>%s</pre>" % value or '')
    
    def _has_changed(self, initial, data):
        return False

class QueryInline(admin.TabularInline):
    model = Query
    can_delete = False

    def queryset(self, request):
        qs = self.model._default_manager.get_query_set()
        qs = qs.order_by('-id')[:10]
        return qs

class StackAdmin(admin.ModelAdmin):
    list_display = ("hash", "total_duration", "total_cost", "count", "last_stack_line")
    readonly_fields = ("hash", "total_duration", "total_cost", "count")
    inlines = [QueryInline]

    formfield_overrides = {
        models.TextField: {'widget': ReadOnlyWidget},
    }


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(StackAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    actions = ['delete_samples']

    def delete_samples(self, request, queryset):
        stacks = list(Stack.objects.all())
        Query.objects.all().delete()
        for stack in stacks:
            try:
                stack.delete()
            except:
                pass
    delete_samples.short_description = "Delete all samples"

admin.site.register(Stack, StackAdmin)

class QueryAdmin(admin.ModelAdmin):
    list_display = ("sql", "duration", "cost")
    readonly_fields = ("sql", "duration", "cost", "stack", "params")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Query, QueryAdmin)

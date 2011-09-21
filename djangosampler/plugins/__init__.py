# Plugin detection and installation module
import sys

from django.conf import settings

def _get_plugin_modules():
    plugins = getattr(settings, 'DJANGO_SAMPLER_PLUGINS', ())
    for plugin_name in plugins:
        module_name, class_name = plugin_name.rsplit('.', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        plugin = getattr(module, class_name)
        yield plugin

def install_plugins():
    for plugin in _get_plugin_modules():
        plugin.install()

def get_view_addons(query_type):
    addons = []
    for plugin in _get_plugin_modules():
        if hasattr(plugin, 'get_query_view_addons'):
            addon = plugin.get_query_view_addons().get(query_type, None)
            if addon:
                addons.append(addon)
    return addons


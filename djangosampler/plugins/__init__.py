# Plugin detection and installation module
import sys

from django.conf import settings

def install_plugins():
    plugins = getattr(settings, 'DJANGO_SAMPLER_PLUGINS', ())
    for plugin_name in plugins:
        module_name, class_name = plugin_name.rsplit('.', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        plugin = getattr(module, class_name)
        plugin.install()


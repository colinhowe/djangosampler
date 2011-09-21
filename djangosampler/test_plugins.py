from django.conf import settings
from django.test import TestCase

from plugins import install_plugins

class DummyPlugin(object):
    @staticmethod
    def install():
        DummyPlugin.install_called = True

    


class TestPlugins(TestCase):
    def setUp(self):
        DummyPlugin.install_called = False
        DummyPlugin.tag_trace_called = None

    def test_install_plugins(self):
        settings.DJANGO_SAMPLER_PLUGINS = ('djangosampler.test_plugins.DummyPlugin', )
        install_plugins()

        self.assertTrue(DummyPlugin.install_called)

from django.conf import settings
from django.test import TestCase

from plugins import install_plugins

import patch

class DummyPlugin(object):
    @staticmethod
    def install():
        DummyPlugin.install_called = True

    @staticmethod
    def tag_trace(trace):
        DummyPlugin.tag_trace_called = trace
        return None


class TestPlugins(TestCase):
    def setUp(self):
        DummyPlugin.install_called = False
        DummyPlugin.tag_trace_called = None

    def test_install_plugins(self):
        settings.DJANGO_SAMPLER_PLUGINS = ('djangosqlsampler.test_plugins.DummyPlugin', )
        install_plugins()

        self.assertTrue(DummyPlugin.install_called)

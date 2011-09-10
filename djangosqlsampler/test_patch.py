from django.conf import settings
from django.test import TestCase

import patch

class TestSamplingCursorWrapper(TestCase):
    def test_calculate_cost(self):
        settings.SQL_SAMPLE_COST = None
        wrapper = patch.SamplingCursorWrapper(None, None)
        self.assertEquals(0.0, wrapper._calculate_cost(1))

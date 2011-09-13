from django.conf import settings
from django.test import TestCase

import sampler

class TestSampler(TestCase):
    def test_calculate_cost(self):
        settings.DJANGO_SAMPLER_USE_COST = None
        self.assertEquals(0.0, sampler._calculate_cost(1))

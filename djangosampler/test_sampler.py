from django.conf import settings
from django.test import TestCase

import sampler
import models

class TestSampler(TestCase):
    def test_calculate_cost(self):
        settings.DJANGO_SAMPLER_USE_COST = None
        self.assertEquals(0.0, sampler._calculate_cost(1))

    def test_sample(self):
        settings.DJANGO_SAMPLER_USE_COST = True
        sampler.sample('sql', 'SELECT 1', 1, [])

        query = models.Query.objects.get()
        self.assertEquals('sql', query.query_type)
        self.assertEquals('SELECT 1', query.query)

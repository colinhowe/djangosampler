from django.conf import settings

if getattr(settings, 'SQL_SAMPLE_FREQ', 0):
    import patch

VERSION = '0.1.3'

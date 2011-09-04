from django.conf import settings

if settings.SQL_SAMPLE_FREQ:
    import patch

VERSION = 0.1

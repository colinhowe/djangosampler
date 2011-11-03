# Script lovingly influenced by the Pinax test running script
import optparse
import os
import sys

from django.conf import settings
from django.core.management import call_command

def setup_test_environment():
    os.environ['PYTHONPATH'] = os.path.abspath(__file__)
    
    settings.configure(**{
        "DATABASES": {
            "default": {
                "ENGINE": "sqlite3",
            },
        },
        "INSTALLED_APPS": ("djangosampler", ),
    })


def main():
    
    usage = "%prog [options]"
    parser = optparse.OptionParser(usage=usage)
    
    parser.add_option("-v", "--verbosity",
        action = "store",
        dest = "verbosity",
        default = "0",
        type = "choice",
        choices = ["0", "1", "2"],
        help = "verbosity level; 0=minimal output, 1=normal output, 2=all output",
    )
    parser.add_option("--coverage",
        action = "store_true",
        dest = "coverage",
        default = False,
        help = "hook in coverage during test suite run and save out results",
    )
    
    options, _ = parser.parse_args()
    
    if options.coverage:
        try:
            import coverage
        except ImportError:
            sys.stderr.write("coverage is not installed.\n")
            sys.exit(1)
        else:
            cov = coverage.coverage(auto_data=True)
            cov.start()
    else:
        cov = None
    
    setup_test_environment()
    
    call_command("test", verbosity=int(options.verbosity))
    
    if cov:
        cov.stop()
        cov.save()


if __name__ == "__main__":
    main()

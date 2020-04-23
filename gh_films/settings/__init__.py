import sys

from .common import *

try:
    from .local import *
except ImportError:
    pass

if "test" in sys.argv:
    try:
        from .tests import *
    except ImportError:
        pass

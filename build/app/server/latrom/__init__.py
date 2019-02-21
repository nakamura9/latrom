from .base import *

PRODUCTION = True


if PRODUCTION:
    from .production import *

else:
    from .development import *
    
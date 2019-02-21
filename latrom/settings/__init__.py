from .base import *

PRODUCTION = False

if PRODUCTION:
    from latrom.settings.production import *

else:
    from latrom.settings.development import *
    
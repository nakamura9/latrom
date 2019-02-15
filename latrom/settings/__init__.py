PRODUCTION = False

if PRODUCTION:
    from latrom.settings.production_settings import *

else:
    from latrom.settings.dev_settings import *
    
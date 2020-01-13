from .base import *
import os 

PRODUCTION = os.path.exists('deploy.txt')

if PRODUCTION:
    from latrom.settings.production import *

else:
    from latrom.settings.development import *
    
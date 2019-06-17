import os 

os.environ['WERKZEUG_RUN_MAIN'] = 'true'


from flask import Flask

app =  Flask(__name__)


#for disabling the logger
# import logging
# log = logging.getLogger('werkzeug')
# log.disabled = True
# app.logger.disabled = True

from server import routes
from common_data.models import GlobalConfig
from background_task import background
import requests
import urllib
import json
import logging 
import datetime
from tkinter import filedialog


logger =logging.getLogger(__name__)


def license_verification_func(license, url):
    print(f'License checked at: {datetime.datetime.now().time().strftime("%H:%M")}')
    config = GlobalConfig.objects.first()
    try:
        #nakamura9.pythonanywhere.com
        resp = requests.get(url, 
            params={
            'info': urllib.parse.quote(json.dumps({
                'customer_id': license['license']['customer_id'],
                'signature': license['signature'],
                'hardware_id': config.hardware_id
            }))
        })
    except requests.ConnectionError:
        logger.critical('the license check failed because of network '
            'connectivity')
        return
       
    if resp.status_code == 200:
        if json.loads(resp.content)['status'] == 'valid':
            config.last_license_check = datetime.date.today()
            config.verification_task_id = ""
            config.save()
        else:
            logger.critical(resp.content)
            logger.critical(f'license check failed because of response: {json.loads(resp.content)["status"]}')
            
        
    else:
        logger.critical(f'license check failed from licensing server. status code:{resp.status_code}.')


@background(schedule=60)
def remote_license_verification(license, 
        url='http://nakamura9.pythonanywhere.com/validate'):
    # ^ for testing purposes
    
    license_verification_func(license, url)



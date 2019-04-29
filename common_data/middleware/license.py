from django.http import HttpResponseRedirect
import json
import hashlib
import datetime
import requests
import hmac 
import time
import urllib
from common_data.models import GlobalConfig
from latrom import settings
##%%
import logging 
from background_task import background

logger =logging.getLogger(__name__)

class UserTrackerException(Exception):
    pass

class UserInfo(object):
    def __init__(self, user, source_ip):
        self.user = user
        self.last_request = time.time()
        self.source_ip = source_ip

    def verify_request(self, request):
        now = time.time()
        if now - self.last_request > 300:
            self.source_ip = request.META['REMOTE_ADDR']
            self.last_request = now
        else:
            if self.source_ip != request.META['REMOTE_ADDR']:
                logger.critical('The same user is using multiple machines')
                raise UserTrackerException(
                    "The same user is using multiple addresses")

            else:
                self.last_request = now

class UserTracker(object):
    def __init__(self):
        self.users = []
        self.users_info = []

        with open('license.json') as f:
            license = json.load(f)
            self.MAX_USERS = license['license']['number_users']

    def track_user(self, request):
        user = request.user
        if user in self.users:
            info = self.get_user_info(user)
            info.verify_request(request)
            
        else:
            if len(self.users) >= self.MAX_USERS:
                logger.critical('More users than licensed are logging in to the server')
                raise UserTrackerException(
                    "More users than allowed are logged in")
            self.add_user(user, request)

    def get_user_info(self, user):
        for info in self.users_info:
            if info.user == user:
                return info

        return None

    def add_user(self, user, request):
        self.users.append(user)
        self.users_info.append(
            UserInfo(user, request.META["REMOTE_ADDR"]))

TRACKER = UserTracker()

class LicenseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        "map each user to a session id"
        "check the number of users that can be logged in"


        if not request.path.startswith('/base/license-error'):
            try:
                TRACKER.track_user(request)
            except UserTrackerException:
                return HttpResponseRedirect('/base/license-error/users')
            
            if  'api' in request.path:
                return self.get_response(request)

            license = None
            try:
                with open('license.json', 'r') as f:
                    license = json.load(f)
            
            except FileNotFoundError:
                logger.critical('The license file is not found')
                return HttpResponseRedirect('/base/license-error-page')

            data_string = json.dumps(license['license']) # + os.environ['django_token]
            byte_data = bytes(data_string, 'ascii')
            hash = hashlib.sha3_512(byte_data).hexdigest()

            if not hmac.compare_digest(hash, license['signature']):
                logger.critical('the license hash check has failed')
                return HttpResponseRedirect('/base/license-error-page')


            #check with remote server every three days
            config = GlobalConfig.objects.get(pk=1)
            #if not settings.DEBUG and \
            if (config.last_license_check == None or \
                    (datetime.date.today() - \
                    config.last_license_check).days > 2):
                # check if a pending task for verification has been generated
                # there are 3 levels of verification id
                # -1 pending
                # 0 success
                # failure
                # empty string means a new task needts to be scheduled
                print('checking ', config.verification_task_id)
                if config.verification_task_id == '1':
                    return HttpResponseRedirect(
                            '/base/license-error-page')
                elif config.verification_task_id == "0":
                        config.verification_task_id = ""
                        config.last_license_check = datetime.date.today()
                        config.save()
                elif config.verification_task_id == '':
                    # if not generate that task and store the task id
                    print('setup')
                    remote_license_verification(license)
                    config.verification_task_id = '-1'
                    config.save()
                elif config.verification_task_id == '-1':
                    self.get_response(request)

                else:
                    config.verification_task_id = ""
                    config.save()

        response = self.get_response(request)

        return response

@background(schedule=1)
def remote_license_verification(license):
    config = GlobalConfig.objects.first()
    try:
        print(license)
        resp = requests.get('http://nakamura9.pythonanywhere.com/validate', 
            params={
            'info': urllib.parse.quote(json.dumps({
                'customer_id': license['license']['customer'],
                'signature': license['signature'],
                'hardware_id': config.hardware_id
            }))
        })
    except requests.ConnectionError:
        logger.critical('the license check failed because of network '
            'connectivity')
        config.verification_task_id = "1"
        config.save()
       
    if resp.status_code == 200 and \
            json.loads(resp.content)['status'] == 'valid':
        config.last_license_check = datetime.date.today()
        config.verification_task_id = "0"
        config.save()
        
    else:
        logger.critical('license check failed from licensing server')
        config.verification_task_id = "1"
        config.save()

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
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
import os
from common_data.tasks import remote_license_verification
from background_task.models import Task
from background_task.models_completed import CompletedTask
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
            
            if  'api' in request.path or \
                request.path.startswith('/admin') or \
                request.path.startswith('/base/reset-license-check'):
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
            if not settings.DEBUG and (config.last_license_check == None or \
                    (datetime.date.today() - \
                    config.last_license_check).days > 2):
                #print((datetime.date.today() - config.last_license_check).days)
                print('checking ', config.verification_task_id)
                
                if config.verification_task_id == '':
                    # if not generate that task and store the task id
                    print('setup')
                    task = remote_license_verification(license)
                    config.verification_task_id = task.task_hash
                    config.save()
                    return self.get_response(request)

                else:
                    print(config.verification_task_id)
                    if CompletedTask.objects.filter(
                            task_hash=config.verification_task_id).exists():
                        task = CompletedTask.objects.filter(
                            task_hash=config.verification_task_id).latest('pk')
                        if task.attempts > 0:
                            print('completed')
                            return HttpResponseRedirect(
                                '/base/license-error-page')
                        else:
                            print('no attempts')
                            return self.get_response(request)
                    else:
                        print('no task')
                        return self.get_response(request)

        return self.get_response(request)



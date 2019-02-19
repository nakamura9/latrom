from django.http import HttpResponseRedirect
import json
import hashlib
import hmac 
import time

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
                return HttpResponseRedirect('/base/license-error-users')
            
            license = None
            try:
                with open('license.json', 'r') as f:
                    license = json.load(f)
            
            except FileNotFoundError:
                return HttpResponseRedirect('/base/license-error-page')

            data_string = json.dumps(license['license']) # + os.environ['django_token]
            byte_data = bytes(data_string, 'ascii')
            hash = hashlib.sha3_512(byte_data).hexdigest()

            if not hmac.compare_digest(hash, license['signature']):
                return HttpResponseRedirect('/base/license-error-page')

        response = self.get_response(request)

        return response

    
import json

from django.test import TestCase, Client
from django.contrib.auth.models import User
from messaging.models import *
from common_data.tests import create_test_common_entities

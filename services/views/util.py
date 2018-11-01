
from django.contrib.auth.mixins import UserPassesTestMixin

class ServiceCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser or \
                self.request.user.employee.is_serviceperson:
            return True
        else:
            return False

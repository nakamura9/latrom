
from django.contrib.auth.mixins import UserPassesTestMixin

class ServiceCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif hasattr(self.request.user, 'serviceperson') and \
                self.request.user.employee.is_service_person:
            return True
        else:
            return False

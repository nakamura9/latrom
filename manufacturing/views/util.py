from django.contrib.auth.mixins import UserPassesTestMixin

class ManufacturingCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser or \
        (hasattr(self.request.user, 'employee') and self.request.user.employee.is_manufacturing_associate):
            return True
        return False
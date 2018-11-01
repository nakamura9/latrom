from django.contrib.auth.mixins import UserPassesTestMixin

class AdministratorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser or \
        self.request.user.employee.is_payroll_officer:
            return True
        return False
from django.contrib.auth.mixins import UserPassesTestMixin

class AdministratorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False
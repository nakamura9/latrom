from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

class UserTestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # TODO add manufacturing
        if request.user.is_superuser or \
                request.path.startswith("/login") or \
                request.path.startswith("/base") or \
                request.path.startswith("/messaging") or \
                request.path.startswith("/planner"):
            return self.get_response(request)
        
        elif hasattr(request.user, 'employee'):
            if request.path.startswith("/invoicing") and \
                    request.user.employee.is_sales_rep:
                return self.get_response(request)

            elif request.path.startswith("/inventory") and \
                    request.user.employee.is_inventory_controller:
                return self.get_response(request)

            elif request.path.startswith("/accounting") and \
                    request.user.employee.is_bookkeeper:
                return self.get_response(request)

            elif request.path.startswith("/employees") and \
                    request.user.employee.is_payroll_officer:
                return self.get_response(request)

            elif request.path.startswith("/services") and \
                    request.user.employee.is_serviceperson:
                return self.get_response(request)

            else:
                return HttpResponseRedirect(
                "/login/")

        else:
            return HttpResponseRedirect(
                "/login/")
        
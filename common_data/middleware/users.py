from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages

class UserTestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        '''
        Middleware that evaluates a requests user and determines whether the 
        user should be granted access to the page.
        Conditions:
            1. the url is publicly available according to exempted urls
            2. the url is one of base, login, calendar, messaging, media or 
                calendar.
            3. If the request user has an employee:
                a. checks if the employee has certain privileges that match the 
                    page requested e.g. invoicing -> sales rep.
                b. the employee is trying to access employee portal pages 
            4. Redirects users to login page if all conditions are not met
        '''

        redirect = request.META.get('HTTP_REFERER', None)

        exempted_urls = [
            '/employees/portal/login',
            '/employees/leave-request',
        ]

        exempted_base_urls = [
            '/employees/portal/dashboard/',
            '/employees/leave-calendar/',
            '/employees/employee-detail/',
            '/employees/employee-portal-update/',
            '/employees/list-pay-slips/',
            '/employees/pay-slip-detail/',
            '/employees/pay-slip-pdf/',
            '/employees/time-logger/',
            '/employees/time-logger-success/'

        ]

        # TODO add manufacturing
        if request.user.is_superuser or \
                request.path.startswith("/login") or \
                request.path.startswith("/base") or \
                request.path.startswith("/messaging") or \
                request.path.startswith("/planner") or \
                request.path.startswith("/media") or \
                request.path.startswith("/calendar") or \
                'api' in request.path or \
                request.path in exempted_urls:
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

            elif request.path.startswith("/employees"):
                if request.user.employee.is_payroll_officer:
                    return self.get_response(request)
                elif any([request.path.startswith(path) \
                    for path in exempted_base_urls]):
                        return self.get_response(request)

                else:
                    messages.info(request, "The currently logged in user does not have the appropriate permissions to access this feature")
                    return HttpResponseRedirect(
                        "/login/?next={}".format(redirect) if redirect else "/login/")

            elif request.path.startswith("/services") and \
                    request.user.employee.is_serviceperson:
                return self.get_response(request)

            else:
                messages.info(request, "The currently logged in user does not have the appropriate permissions to access this feature")
                return HttpResponseRedirect(
                "/login/?next={}".format(redirect) if redirect else "/login/")

        else:
            messages.info(request, "The currently logged in user does not have the appropriate permissions to access this feature")
            return HttpResponseRedirect(
                "/login/?next={}".format(redirect) if redirect else "/login/")
        
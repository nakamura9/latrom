"""latrom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import static
from django.contrib import admin
from django.urls import include, re_path
from planner.views import ReactCalendar
from common_data.urls import workflow
urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r'^$', workflow),
    re_path(r'^base/', include(('common_data.urls', 'base'), namespace='base')),
    re_path(r'^invoicing/', include(("invoicing.urls", 'invoicing'), namespace="invoicing")),
    re_path(r'^accounting/', include(("accounting.urls", 'accounting'), namespace="accounting")),
    re_path(r'^inventory/', include(("inventory.urls", 'inventory'), namespace="inventory")),
    re_path(r'^employees/', include(("employees.urls", 'employees'), namespace="employees")),
    re_path(r'^services/', include(("services.urls", 'services'), namespace="services")),
    re_path(r'^planner/', include(("planner.urls", 'planner'), namespace="planner")),
    re_path(r'^messaging/', include(("messaging.urls", 'messaging'), namespace="messaging")),
    re_path(r'^manufacturing/', include(("manufacturing.urls", 'manufacturing'), namespace="manufacturing")),
    re_path(r'^calendar/*', ReactCalendar.as_view()),
    re_path(r'^', include('django.contrib.auth.urls'))
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

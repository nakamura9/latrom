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
from django.contrib import admin
from django.conf.urls import url,  include, static
from django.conf import settings

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^base/', include('common_data.urls', namespace='base')),
    url(r'^invoicing/', include("invoicing.urls", namespace="invoicing")),
    url(r'^accounting/', include("accounting.urls", namespace="accounting")),
    url(r'^inventory/', include("inventory.urls", namespace="inventory")),
    url(r'^employees/', include("employees.urls", namespace="employees")),
    url(r'^services/', include("services.urls", namespace="services")),
    url(r'^', include('django.contrib.auth.urls'))
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

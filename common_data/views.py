from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
import os
from django.urls import reverse_lazy
from accounting.models import Journal
from invoicing.models import SalesConfig


class WorkFlowView(TemplateView):
    template_name = os.path.join("common_data", "workflow.html")

class ReactTest(TemplateView):
    template_name = os.path.join("common_data", "react_test.html")


def config_JSON_API(request):
    return JsonResponse(SalesConfig.get_config_dict())

def get_logo_url(request):
    return JsonResponse({'url': SalesConfig.logo_url() })
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
import os
from django.urls import reverse_lazy
from accounting.models import Journal
from utilities import load_config

class WorkFlowView(TemplateView):
    template_name = os.path.join("common_data", "workflow.html")

class ReactTest(TemplateView):
    template_name = os.path.join("common_data", "react_test.html")


def config_JSON_API(request):
    return JsonResponse(load_config())

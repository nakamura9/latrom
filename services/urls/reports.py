from django.urls import re_path, path
import services

report_urls = [
    path("reports/unbilled-costs-by-job/", 
            services.views.UnbilledCostsByJobReportView.as_view(), 
            name="reports-unbilled-costs-by-job"),
    path("reports/unbilled-costs-by-job-pdf/<str:start>/<str:end>/", 
            services.views.UnbilledCostsByJobPDFView.as_view(), 
            name="reports-unbilled-costs-by-job-pdf"),
    path("reports/forms/unbilled-costs-by-job/", 
            services.views.UnbilledCostsByJobReportFormView.as_view(), 
            name="reports-unbilled-costs-by-job-form"),
    path('reports/forms/job-profitability/', 
        services.views.reports.JobProfitabilityReportFormView.as_view(), 
        name="reports-job-profitability-form"),
    path('reports/job-profitability/', 
        services.views.reports.JobProfitabilityReport.as_view(), 
        name="reports-job-profitability"),
    path('reports/job-profitability-pdf/<str:start>/<str:end>/', 
        services.views.reports.JobProfitabilityPDFView.as_view(), 
        name="reports-job-profitability-pdf"),
    re_path(r'^reports/forms/service-person-utilization/?$', 
        services.views.reports.ServicePersonUtilizationFormView.as_view(), 
        name="reports-service-person-utilization-form"),
    re_path(r'^reports/service-person-utilization/?$', 
        services.views.reports.ServicePersonUtilizationReport.as_view(), 
        name="reports-service-person-utilization"),
    re_path(r'^reports/service-person-utilization/pdf/(?P<start>[\w %]+)/(?P<end>[\w %]+)/?$', 
        services.views.reports.ServicePersonUtilizationReportPDFView.as_view(), 
        name="reports-service-person-utilization-pdf")
]
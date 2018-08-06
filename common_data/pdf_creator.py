import os
from django.conf import settings
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
from invoicing.views import SalesInvoiceDetailView

REPORT_TEMPLATES = {
    'sales_invoice': SalesInvoiceDetailView 
}

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources.
    This function is taken from an online source that provided xhtml2pdf.
    """
    # use short variable names
    sUrl = settings.STATIC_URL # Typically /static/
    sRoot = settings.STATIC_ROOT # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL # Typically /static/media/
    mRoot = settings.MEDIA_ROOT # Typically /home/userX/project_static/media/
    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def generate_pdf(request, pk=None, view=''):
    global REPORT_TEMPLATES
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s_%s.pdf"' % (view, pk)
    
    # find the template and render it.
    view = REPORT_TEMPLATES.get(view)
    resp = view.as_view()(request, pk=pk)
    resp.render()
    html = resp.content

    # create a pdf
    pisaStatus = pisa.CreatePDF(
    html, dest=response, link_callback=link_callback)
    
    # if error then show some view
    if pisaStatus.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
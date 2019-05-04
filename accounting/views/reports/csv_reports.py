from django.http import HttpResponse
import csv
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
import urllib
import datetime

from .balance_sheet import BalanceSheet
from .trial_balance import TrialBalance
from .profit_and_loss import ProfitAndLossReport
from .account import AccountReport
from .journal import JournalReport
from accounting.models import Account
from django.db.models import Q

def balance_sheet_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'
    
    writer = csv.writer(response)
    string =render_to_string(
        BalanceSheet.template_name, BalanceSheet.common_context({}))
    
    soup = BeautifulSoup(string)
    data = soup.find_all('table')[1]
    rows = data.find_all('tr')

    for row in rows:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 

def trial_balance_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="trial_balance.csv"'
    
    writer = csv.writer(response)
    
    #for headings 
    qs = Account.objects.all().exclude(
            Q(balance=0.0) & Q(control_account=False)).exclude(
                parent_account__isnull=False).order_by('pk')

    
    writer.writerow(['Account Code', 'Account Title', 'Debit', 'Credit'])
    for acc in qs:
        writer.writerow([acc.pk, acc.name, acc.debit, acc.credit])

    return response 

def profit_and_loss_csv(request, start=None, end=None):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="profit_and_loss.csv"'
    
    start = datetime.datetime.strptime(urllib.parse.unquote(start), "%d %B %Y")
    end = datetime.datetime.strptime(urllib.parse.unquote(end), "%d %B %Y")

    writer = csv.writer(response)
    string =render_to_string(
        ProfitAndLossReport.template_name, ProfitAndLossReport.common_context({}
            ,start, end))
    
    soup = BeautifulSoup(string)
    data = soup.find_all('table')[1]

    rows = data.find_all('tr')

    #for headings 
    for row in rows:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 

    
def account_csv_report(request, start=None, end=None, account=None):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="account.csv"'
    start = datetime.datetime.strptime(urllib.parse.unquote(start), "%d %B %Y")
    end = datetime.datetime.strptime(urllib.parse.unquote(end), "%d %B %Y")

    writer = csv.writer(response)
    string =render_to_string(
        AccountReport.template_name, AccountReport.common_context({
            'account': account
            },start, end))
    soup = BeautifulSoup(string)
    data = soup.find_all('table')[1]

    rows = data.find_all('tr')

    #for headings 
    writer.writerow([i.string for i in rows[0].find_all('th')])
    for row in rows[1:]:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 

def journal_csv_report(request, start=None, end=None, journal=None):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="journal_report.csv"'
    start = datetime.datetime.strptime(urllib.parse.unquote(start), "%d %B %Y")
    end = datetime.datetime.strptime(urllib.parse.unquote(end), "%d %B %Y")

    writer = csv.writer(response)
    string =render_to_string(
        JournalReport.template_name, JournalReport.common_context({
            'journal': journal
            },start, end))
    
    soup = BeautifulSoup(string)
    data = soup.find_all('table')[1]

    rows = data.find_all('tr')

    #for headings 
    writer.writerow([i.string for i in rows[0].find_all('th')])
    for row in rows[1:]:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 
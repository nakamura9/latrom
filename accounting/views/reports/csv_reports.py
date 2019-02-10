from django.http import HttpResponse
import csv
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
import urllib
import datetime

from .balance_sheet import BalanceSheet
from .trial_balance import TrialBalance
from .profit_and_loss import ProfitAndLossReport

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
    string =render_to_string(
        TrialBalance.template_name, TrialBalance.common_context({}))
    
    soup = BeautifulSoup(string)
    data = soup.find_all('table')[1]

    rows = data.find_all('tr')

    #for headings 
    writer.writerow([i.string for i in rows[0].find_all('th')])
    for row in rows[1:]:
        writer.writerow([i.string for i in row.find_all('td')])

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

    
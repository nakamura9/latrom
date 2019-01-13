import datetime
from accounting import models 
from django.db.models import Q

class AccountingTaskService(object):
    def __init__(self):
        self.today  = datetime.date.today()

    def run(self):
        print('running accounting services')
        self.run_recurring_expenses()
        self.run_interest_on_accounts()
        

    def run_recurring_expenses(self):
        expenses = models.RecurringExpense.objects.filter(
            Q(expiration_date__gt=self.today) |
            Q(expiration_date__isnull=True)
            )

        for expense in expenses:

            if expense.last_created_date is None:
                # expenses whose start date + cycle exceeds today
                if expense.start_date + datetime.timedelta(
                        days=expense.cycle) >= self.today:
                    expense.create_standalone_expense()
                #expenses
            else:
                if expense.last_created_date + datetime.timedelta(
                        days=expense.cycle) <= self.today:
                    expense.create_standalone_expense()

    def run_interest_on_accounts(self):
        print('accruing interest')
        accounts = models.InterestBearingAccount.objects.all()
        for acc in accounts:
            if acc.should_receive_interest(self.today):
                acc.add_interest()
                acc.last_interest_earned_date = self.today
                acc.save()


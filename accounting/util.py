import datetime
from accounting import models 

class AccountingTaskService(object):
    def __init__(self):
        self.today  = datetime.date.today()

    def run(self):
        self.run_recurring_expenses()
        self.run_interest_on_accounts()
        self.depreciate_assets()

    def run_recurring_expenses(self):
        print('generating recurring expense')
        expenses = models.RecurringExpense.objects.filter(
            expiration_date__gt=self.today)

        for expense in expenses:

            if expense.last_created_date is None:
                # expenses whose start date + cycle exceeds today
                if expense.start_date + datetime.timedelta(
                        days=expense.cycle) >= self.today:
                    expense.create_entry()
                    expense.create_standalone_expense()
                    expense.last_created_date = self.today
                    expense.save()
                #expenses
            else:
                if expense.last_created_date + datetime.timedelta(
                        days=expense.cycle) <= self.today:
                    expense.create_entry()
                    expense.create_standalone_expense()
                    expense.last_created_date = self.today
                    expense.save()

    def run_interest_on_accounts(self):
        print('accruing interest')
        accounts = models.InterestBearingAccount.objects.all()
        for acc in accounts:
            if acc.should_receive_interst(self.today):
                acc.add_interest()
                acc.last_interest_earned_date = self.today
                acc.save()



    def depreciate_assets(self):
        print('depreciating assets')
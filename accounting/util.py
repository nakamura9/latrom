import datetime
from accounting import models 
from django.db.models import Q
from calendar import monthrange
from common_data.utilities import AutomatedServiceMixin


class AccountingTaskService(AutomatedServiceMixin):
    service_name = 'accounting'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.today  = datetime.date.today()

    def _run(self):
        print('running accounting services')
        self.run_recurring_expenses()
        self.run_interest_on_accounts()
        self.depreciate_assets()
        

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


    def depreciate_assets(self):
        print('depreciating assets')
        end_of_month = monthrange(self.today.year, self.today.month)[1]
        if self.today.day == end_of_month:
            #fix # how to make sure each month is depreciated
            for asset in models.Asset.objects.filter(
                    Q(category=1) | 
                    Q(category=2) | 
                    Q(category=4) | 
                    Q(category=5)):
                
                amount = asset.depreciation_for_month(self.today.month, 
                    self.today.year)
                settings = models.AccountingSettings.objects.first()
                bkkpr = models.Bookkeeper.objects.first()
                if settings.default_bookkeeper:
                    created_by= settings.default_bookkeeper
                else:
                    created_by=bkkpr
                    
                j = models.JournalEntry.objects.create(
                        date=self.today,
                        draft=False,
                        memo="Asset depreciation",
                        journal=models.Journal.objects.get(pk=5),
                        created_by=created_by.employee.user
                    )
                j.simple_entry(amount, asset.account, 
                    asset.depreciation_account)
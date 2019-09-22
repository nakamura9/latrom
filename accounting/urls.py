from django.urls import re_path, path
from rest_framework import routers

from accounting import views

tax_router = routers.DefaultRouter()
tax_router.register(r'^api/tax', views.TaxViewset)

settings_router = routers.DefaultRouter()
settings_router.register(r'^api/settings', views.AccountingSettingsAPIView)

account_router = routers.DefaultRouter()
account_router.register(r'^api/account', views.AccountViewSet)


expense_router = routers.DefaultRouter()
expense_router.register(r'^api/expense', views.ExpenseAPIView)


currency_router = routers.DefaultRouter()
currency_router.register(r'^api/currency', views.CurrencyAPIView)

currency_conversion_line_router = routers.DefaultRouter()
currency_conversion_line_router.register(r'^api/currency-conversion-line',
     views.CurrencyConversionLineAPIView)

currency_conversion_table_router = routers.DefaultRouter()
currency_conversion_table_router.register(r'^api/currency-conversion-table',
     views.CurrencyConversionTableAPIView)

bill_urls = [
    path('create-bill/', views.BillCreateView.as_view(), name='create-bill'),
    path('update-bill/<int:pk>', 
        views.BillUpdateView.as_view(), name='update-bill'),
    path('list-bills/', views.BillListView.as_view(), name='list-bills'),
    path('bill-details/<int:pk>', 
        views.BillDetailView.as_view(), name='bill-details'),
    path('create-bill-payment/<int:pk>', 
        views.BillPaymentView.as_view(), name='create-bill-payment'),

]

expense_urls = [
    re_path(r'^expense/create/?$', views.ExpenseCreateView.as_view(), 
        name="expense-create"),
    path('expense/create-multiple/', 
        views.CreateMultipleExpensesView.as_view(), 
        name="create-multiple-expenses"),
    path('expense/import/', 
        views.ImportExpensesView.as_view(), 
        name="import-expenses"),
    re_path(r'^expense/list/?$', views.ExpenseListView.as_view(), 
        name="expense-list"),
    re_path(r'^expense/detail/(?P<pk>[\d]+)/?$', 
        views.ExpenseDetailView.as_view(), name="expense-detail"),
    re_path(r'^expense/delete/(?P<pk>[\d]+)/?$', 
        views.ExpenseDeleteView.as_view(), name="expense-delete"),
    re_path(r'^api/expense/customer/(?P<customer>[\d]+)/?$', 
        views.CustomerExpenseAPIView.as_view())
]

asset_urls = [
    re_path(r'^asset/create/?$', views.AssetCreateView.as_view(), name="asset-create"),
    re_path(r'^asset/list/?$', views.AssetListView.as_view(), 
        name="asset-list"),
    re_path(r'^asset/detail/(?P<pk>[\d]+)/?$', 
        views.AssetDetailView.as_view(), name="asset-detail"),
    re_path(r'^asset/update/(?P<pk>[\d]+)/?$', 
        views.AssetUpdateView.as_view(), name="asset-update"),
]

recurring_expense_urls = [
    re_path(r'^recurring-expense/create/?$',    
        views.RecurringExpenseCreateView.as_view(), 
        name="recurring-expense-create"),
    re_path(r'^recurring-expense/list/?$', 
        views.RecurringExpenseListView.as_view(), 
        name="recurring-expense-list"),
    re_path(r'^recurring-expense/detail/(?P<pk>[\d]+)/?$', 
        views.RecurringExpenseDetailView.as_view(), 
        name="recurring-expense-detail"),
    re_path(r'^recurring-expense/update/(?P<pk>[\d]+)/?$', 
        views.RecurringExpenseUpdateView.as_view(), 
        name="recurring-expense-update"),
    re_path(r'^recurring-expense/delete/(?P<pk>[\d]+)/?$', 
        views.RecurringExpenseDeleteView.as_view(), 
        name="recurring-expense-delete"),
]

report_urls = [
    re_path(r'^balance-sheet/?$', views.BalanceSheet.as_view(), 
        name='balance-sheet'),
    re_path(r'^balance-sheet-pdf/?$', views.BalanceSheetPDFView.as_view(), 
        name='balance-sheet-pdf'),
    re_path(r'^trial-balance/?$', views.TrialBalance.as_view(), 
        name='trial-balance'),
    re_path(r'^trial-balance-pdf/?$', views.TrialBalancePDFView.as_view(), 
        name='trial-balance-pdf'),
    re_path(r'^profit-and-loss/?$', views.ProfitAndLossReport.as_view(), 
        name='profit-and-loss'),
    re_path(r'^profit-and-loss-form/?$', views.ProfitAndLossFormView.as_view(), 
        name='profit-and-loss-form'),
    re_path(r'^csv/profit-and-loss/(?P<start>[\w %]+)/(?P<end>[\w %]+)/?$', 
        views.profit_and_loss_csv, name='profit-and-loss-csv'),
    re_path(r'^pdf/profit-and-loss/(?P<start>[\w %]+)/(?P<end>[\w %]+)/?$', 
        views.ProfitAndLossReportPDFView.as_view(), name='profit-and-loss-pdf'),
    re_path(r'^csv/balance-sheet/?$', views.balance_sheet_csv, 
        name='balance-sheet-csv'),
    re_path(r'^csv/trial-balance/?$', views.trial_balance_csv, 
        name='trial-balance-csv'),
    re_path(r'^journal-form/(?P<pk>[\d]+)/?$', views.JournalFormView.as_view(), name='journal-form'),
    re_path(r'^journal-report/?$', views.JournalReport.as_view(), name='journal-report'),
    re_path(r'^csv/journal-report/(?P<journal>[\d ]+)/(?P<start>[\w %]+)/'
        '(?P<end>[\w %]+)/?$', views.journal_csv_report, 
            name='journal-report-csv'),
    re_path(r'^pdf/journal-report/(?P<journal>[\d ]+)/(?P<start>[\w %]+)/'
        '(?P<end>[\w %]+)/?$', views.JournalReportPDFView.as_view(), 
            name='journal-report-pdf'),
    re_path(r'^account-report-form/(?P<pk>[\d]+)/?$', 
        views.AccountReportFormView.as_view(), name='account-report-form'),
    re_path(r'^account-report/?$', views.AccountReport.as_view(), 
        name='account-report'),
    re_path(r'^csv/account-report/(?P<account>[\d ]+)/(?P<start>[\w %]+)/'
        '(?P<end>[\w %]+)/?$', views.account_csv_report, 
            name='account-report-csv'),
    re_path(r'^pdf/account-report/(?P<account>[\d ]+)/(?P<start>[\w %]+)/'
        '(?P<end>[\w %]+)/?$', views.AccountReportPDFView.as_view(), 
            name='account-report-pdf')
]

account_urls = [
    re_path(r'^create-account/?$', views.AccountCreateView.as_view(), 
        name='create-account'),
    re_path(r'^bulk-create-accounts/?$', 
        views.BulkAccountCreateView.as_view(), 
        name='bulk-create-accounts'),
    re_path(r'^import-accounts-from-excel/?$', 
        views.ImportAccountsView.as_view(), 
        name='import-accounts-from-excel'),
    re_path(r'^account-detail/(?P<pk>[\w]+)/?$', 
        views.AccountDetailView.as_view(), 
        name='account-detail'),
    re_path(r'^account-update/(?P<pk>[\w]+)/?$', 
        views.AccountUpdateView.as_view(), 
        name='account-update'),
    re_path(r'^account-list/?$', views.AccountListView.as_view(), 
        name='account-list'),
    re_path(r'^account/(?P<pk>[\w]+)/entry-list/credit/?$', 
        views.AccountCreditIframeView.as_view(), name="account-credits"),
    re_path(r'^account/(?P<pk>[\w]+)/entry-list/debit/?$', 
        views.AccountDebitIframeView.as_view(), name="account-debits")
        ]

bookkeeper_urls = [
    re_path(r'^create-bookkeeper/?$', views.BookkeeperCreateView.as_view(), 
        name = 'create-bookkeeper'),
    re_path(r'^bookkeeper-list/?$', views.BookkeeperListView.as_view(), 
        name='bookkeeper-list'),
    re_path(r'^bookkeeper/update/(?P<pk>[\w]+)/?$', 
        views.BookkeeperUpdateView.as_view(), name='bookkeeper-update'),
    re_path(r'^bookkeeper/detail/(?P<pk>[\w]+)/?$', 
        views.BookkeeperDetailView.as_view(), name='bookkeeper-detail'),
    re_path(r'^bookkeeper/delete/(?P<pk>[\w]+)/?$', 
        views.BookkeeperDeleteView.as_view(), name='bookkeeper-delete')
]

currency_urls = [
    re_path(r'^currency-converter/?$', views.CurrencyConverterView.as_view(), 
        name='currency-converter'),
    re_path(r'^create-exchange-table/?$', 
        views.ExchangeTableCreateView.as_view(), 
        name='create-exchange-table'),
    re_path(r'^api/update-reference-currency/(?P<table>[\d]+)/'
        '(?P<currency>[\d]+)/?$', 
        views.update_reference_currency),
    re_path(r'^api/create-conversion-line/?$', 
        views.create_exchange_table_conversion_line),
    re_path(r'^api/update-exchange-rate/(?P<line>[\d]+)/?$', 
        views.exchange_rate),
    re_path(r'^create-currency/?$', views.CurrencyCreateView.as_view(), 
        name='create-currency'),
    re_path(r'^update-currency/(?P<pk>[\d]+)?$', 
        views.CurrencyUpdateView.as_view(), name='update-currency'),
    re_path(r'^create-currency-conversion-line/?$', 
        views.CurrencyConversionLineCreateView.as_view(), 
        name='create-currency-conversion-line'),
    re_path(r'^update-currency-conversion-line/(?P<pk>[\d]+)/?$',
        views.CurrencyConversionLineUpdateView.as_view(),
        name='update-currency-conversion-line'),
]

misc_urls = [    
    re_path(r'^transfer/?$', views.AccountTransferPage.as_view(), 
    name='transfer'),
    re_path(r'^create-tax/?$', views.TaxCreateView.as_view(), 
        name='create-tax'),
    re_path(r'^tax-list/?$', views.TaxListView.as_view(), name='tax-list'),
    re_path(r'^delete-tax/(?P<pk>[\w]+)/?$', views.TaxDeleteView.as_view(), 
        name='delete-tax'),
    re_path(r'^update-tax/(?P<pk>[\w]+)/?$', views.TaxUpdateView.as_view(), 
        name='update-tax'),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.AccountConfigView.as_view(), 
        name='config'),
    re_path(r'^direct-payment/?$', views.DirectPaymentFormView.as_view(), 
        name='direct-payment'),
    re_path(r'^(?P<supplier>[\w]+)/direct-payment/?$', 
        views.DirectPaymentFormView.as_view(), name='direct-payment-supplier'),
    re_path(r'^direct-payment-list/?$', views.DirectPaymentList.as_view(), 
        name='direct-payment-list'),
    
    ]

entry_urls = [
    re_path(r'^create-entry/?$', views.JournalEntryCreateView.as_view(), 
        name='create-entry'),
    path('create-multiple-entries/', 
        views.CreateMultipleEntriesView.as_view(), 
        name='create-multiple-entries'),
    path('import-entries-from-excel/', 
        views.ImportTransactionView.as_view(), 
        name='import-entries-from-excel'),
    re_path(r'^compound-entry/?$', views.ComplexEntryView.as_view(), 
        name='compound-entry'),
    re_path(r'^entry-detail/(?P<pk>[\w]+)/?$', 
        views.JournalEntryDetailView.as_view(), 
        name='entry-detail'),
    re_path(r'^verify-entry/(?P<pk>[\w]+)/?$', 
        views.verify_entry,
        name='verify-entry'),
]

journal_urls = [
    re_path(r'^create-journal/?$', views.JournalCreateView.as_view(), 
        name='create-journal'),
    re_path(r'^journal-list/?$', views.JournalListView.as_view(), 
        name='journal-list'),
    re_path(r'^journal-detail/(?P<pk>[\w]+)/?$', 
        views.JournalDetailView.as_view(), 
        name='journal-detail'),
    re_path(r'^journal/(?P<pk>[\w]+)/entry-list/?$', 
        views.JournalEntryIframeView.as_view(), name="journal-entries")
    ]


urlpatterns =[
    re_path(r'^config-wizard/?$', views.ConfigWizard.as_view(), name='config-wizard'),
    re_path(r'^$', views.Dashboard.as_view(), name='dashboard'),
    re_path(r'^async-dashboard/$', views.AsyncDashboard.as_view(), name='async-dashboard'),
] + tax_router.urls +  misc_urls + account_urls  + journal_urls + \
    entry_urls  + account_router.urls  + expense_urls + report_urls + \
    expense_router.urls + recurring_expense_urls + asset_urls + \
    bookkeeper_urls + currency_urls + currency_router.urls + \
    currency_conversion_line_router.urls + currency_conversion_table_router.urls + settings_router.urls + \
    bill_urls
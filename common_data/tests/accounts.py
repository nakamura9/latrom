def create_accounts(cls):
    from accounting.tests.model_util import AccountingModelCreator
    return AccountingModelCreator(cls).create_accounts()
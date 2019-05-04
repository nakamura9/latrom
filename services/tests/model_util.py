from services.models import *
import datetime

class ServiceModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_procedure(self):
        self.cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )

    def create_category(self):
        self.cls.service_category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )

    def create_service(self):
        if not hasattr(self.cls, 'procedure'):
            self.create_procedure()

        if not hasattr(self.cls, 'service_category'):
            self.create_category()

        self.cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=self.cls.service_category,
            procedure=self.cls.procedure,
            frequency='once',
            is_listed=True
        )


    def create_service_work_order(self):
        self.cls.service_work_order = ServiceWorkOrder.objects.create(
            date = datetime.date.today(),
            time=datetime.datetime.now().time(),
            status='requested'
        )

        return self.cls.service_work_order
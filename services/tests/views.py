from django.contrib.auth.models import User
from django.test import TestCase, Client 
from django.test.client import RequestFactory
import inventory
from employees.tests.models import create_test_employees_models
from employees.models import Employee
from services.models import *
import urllib
import json
import datetime
from common_data.tests import create_test_common_entities, create_test_user
from django.shortcuts import reverse
from services.views import (JobProfitabilityPDFView,
                            ServicePersonUtilizationReportPDFView,
                            UnbilledCostsByJobPDFView)


TODAY = datetime.date.today()

class BasicServiceViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_user(cls)
        #inventory.tests.models.create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            **{'name': 'name', 'description': 'description'}   
        )
        create_test_common_entities(cls)
        cls.settings_ = ServicesSettings.objects.create(
            is_configured =True
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_dashboard_page(self):
        
        resp = self.client.get('/services/')
        self.assertEqual(resp.status_code, 200)
        self.settings_.is_configured = False
        self.settings_.save()

        resp = self.client.get('/services/')
        self.assertEqual(resp.status_code, 302)
        self.settings_.is_configured = True
        self.settings_.save()



    def test_get_create_category_page(self):
        resp = self.client.get('/services/create-category/')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_category_page(self):
        resp = self.client.post('/services/create-category/',
            data={'name': 'name', 'description': 'description'})
        self.assertEqual(resp.status_code, 302)

    def test_get_category_update_page(self):
        resp = self.client.get('/services/update-category/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_category_update_page(self):
        resp = self.client.post('/services/update-category/1',
            data={'name': 'name', 'description': 'other description'})
        self.assertEqual(resp.status_code, 302)

    def test_get_category_detail_page(self):
        resp = self.client.get('/services/category-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_category_list_page(self):
        resp = self.client.get('/services/category-list')
        self.assertEqual(resp.status_code, 200)


class ServicePersonnelViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_common_entities(cls)
        inventory.tests.models.create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            **{'name': 'name', 'description': 'description'}   
        )
        cls.service_person = ServicePerson.objects.create(
            employee=cls.employee
        )
        cls.service_team = ServiceTeam.objects.create(
            name="name",
            description="description"
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_service_person_creation_page(self):
        resp = self.client.get('/services/service-person-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_person_creation_page(self):
        obj = Employee.objects.create(
                first_name = 'First',
                last_name = 'Last',
                address = 'Model test address',
                email = 'test@mail.com',
                phone = '1234535234',
                pay_grade = self.grade
            )
        resp = self.client.post('/services/service-person-create', 
            data={
                'employee': obj.pk,
                'is_manager': True,
                'can_authorize_equipment_requisitions': True,
                'can_authorize_consumables_requisitions': True,
            })
        obj.delete()
        self.assertEqual(resp.status_code, 302)

    def test_get_service_person_update_page(self):
        resp = self.client.get('/services/service-person-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_person_update_page(self):
        resp = self.client.post('/services/service-person-update/1', 
            data={
                'is_manager': False,
                'can_authorize_equipment_requisitions': True,
                'can_authorize_consumables_requisitions': True,
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_service_person_detail_page(self):
        resp = self.client.get('/services/service-person-dashboard/1')
        self.assertEqual(resp.status_code, 200)

    def test_service_person_list_page(self):
        resp = self.client.get('/services/service-person-list/')
        self.assertEqual(resp.status_code, 200)

    def test_get_team_create_page(self):
        resp = self.client.get('/services/team-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_team_create(self):
        resp = self.client.post('/services/team-create', data={
            'name': 'name',
            'description': 'descritopm',
            'manager': 1,
            'members': urllib.parse.quote(json.dumps([
                '1 - Service'
            ]))
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_team_update_page(self):
        resp = self.client.get('/services/team-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_team_update(self):
        resp = self.client.post('/services/team-update/1', data={
            'name': 'name',
            'description': 'descritopm',
            'manager': 1,
            'members': urllib.parse.quote(json.dumps([
                '1 - Service'
            ]))
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_service_team_detail_page(self):
        resp = self.client.get('/services/team-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_team_list_page(self):
        resp = self.client.get('/services/team-list')
        self.assertEqual(resp.status_code, 200)
     

class ServiceProcedureViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_common_entities(cls)
        create_test_employees_models(cls)
        inventory.tests.models.create_test_inventory_models(cls)
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name='Name',
            reference="ref",
            description="desc",
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_service_procedure_page(self):
        resp = self.client.get('/services/create-procedure')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_procedure(self):
        resp = self.client.post('/services/create-procedure', 
            data={
                'tasks': urllib.parse.quote(json.dumps([
                    'some task'
                ])),
                'equipment': urllib.parse.quote(json.dumps([
                    '1 - item'
                ])),
                'consumables': urllib.parse.quote(json.dumps([
                    '1 - item'
                ])),
                'as_checklist': True,
                'name': 'name',
                'description': 'some description',
                'reference': 'ref',
                'author': 1
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_list_procedure_page(self):
        resp = self.client.get('/services/list-procedures')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_procedure_update_page(self):
        resp = self.client.get('/services/procedure-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_procedure_update(self):
        resp = self.client.post('/services/procedure-update/1', 
            data={
                'tasks': urllib.parse.quote(json.dumps([
                    'some task'
                ])),
                'equipment': urllib.parse.quote(json.dumps([
                    '1 - item'
                ])),
                'consumables': urllib.parse.quote(json.dumps([
                    '1 - item'
                ])),
                'as_checklist': True,
                'name': 'name',
                'description': 'some description',
                'reference': 'ref',
                'author': 1
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_procedure_detail_page(self):
        resp = self.client.get('/services/procedure-detail/1')
        self.assertEqual(resp.status_code, 200)

    
class RequisitionViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_common_entities(cls)
        create_test_employees_models(cls)
        inventory.tests.models.create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )
        cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=cls.category,
            procedure=cls.procedure,
            frequency='once',
            is_listed=True
        )

        cls.wr = WorkOrderRequest.objects.create(
            service = cls.service,
            status="request",
        )
        cls.wo = ServiceWorkOrder.objects.create(
            date=str(TODAY),
            time="17:00",
            description="desc",
            status="progress",
            completed=datetime.datetime.now(),
            expected_duration=datetime.timedelta(seconds=3600),
            works_request=cls.wr
        )
        cls.eq_requisition = EquipmentRequisition.objects.create(
            date=TODAY,
            reference="ref",
            requested_by=cls.employee
        )

        cls.con_requsition = ConsumablesRequisition.objects.create(
            date=TODAY,
            reference="ref",
            requested_by=cls.employee
        )
        cls.employee.user=User.objects.create_user(username="user2", password="123")
        cls.employee.save()

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_equipment_requisition_page(self):
        resp = self.client.get('/services/equipment-requisition-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_equipment_requisition_page(self):
        resp = self.client.post('/services/equipment-requisition-create', 
            data={
                'equipment': urllib.parse.quote(json.dumps([{
                    'item': '1 - item',
                    'condition': 'good',
                    'quantity': 1
                }])),
                'date': TODAY,
                'warehouse': 1,
                'reference': 'ref',
                'requested_by': 1,
                "work_order": self.wo.pk
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_equipment_requsition_list(self):
        resp = self.client.get('/services/equipment-requisition-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_equipment_requisition_detail(self):
        resp = self.client.get('/services/equipment-requisition-auth-view/1')
        self.assertEqual(resp.status_code, 200)

    def test_equipment_requisition_release(self):
        resp = self.client.post('/services/equipment-requisition-release/1',
            data={
                'user': self.employee.user.pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(EquipmentRequisition.objects.first().released_by, 
            self.employee)

    def test_equipment_requisition_authorize(self):
        resp = self.client.post('/services/equipment-requisition-authorize/1',
            data={
                'user': self.employee.user.pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(EquipmentRequisition.objects.first().authorized_by, 
            self.employee)

    def test_get_consumable_requisition_page(self):
        resp = self.client.get('/services/consumable-requisition-create')
        self.assertEqual(resp.status_code, 200)

    def test_post_consumable_requisition_page(self):
        resp = self.client.post('/services/consumable-requisition-create', 
            data={
                'consumables': urllib.parse.quote(json.dumps([{
                    'item': '1 - item',
                    'unit': '1 - something',
                    'quantity': 1
                }])),
                'date': TODAY,
                'warehouse': 1,
                'reference': 'ref',
                'requested_by': 1,
                'work_order': self.wo.pk
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_consumable_requsition_list(self):
        resp = self.client.get('/services/consumable-requisition-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_consumable_requisition_detail(self):
        resp = self.client.get('/services/consumable-requisition-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_consumable_requisition_release(self):
        resp = self.client.post('/services/consumable-requisition-release/1',
            data={
                'user': self.employee.user.pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ConsumablesRequisition.objects.first().released_by, 
            self.employee)

    def test_get_consumable_requisition_get_auth(self):
        resp = self.client.get('/services/consumable-requisition-auth-view/1')
        self.assertEqual(resp.status_code, 200)

    def test_consumable_requisition_authorize(self):
        resp = self.client.post('/services/consumable-requisition-authorize/1',
            data={
                'user': self.employee.user.pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ConsumablesRequisition.objects.first().authorized_by, self.employee) 

    def test_get_equipment_return_page(self):
        resp = self.client.get('/services/equipment-return/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_equipment_return_page(self):
        resp = self.client.post('/services/equipment-return/1', data={
            "received_by": self.employee.pk,
            "requisition": 1,
            "password": "123",
            "return_date": TODAY,
            "work_order": 1
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_equipment_detail_page(self):
        resp = self.client.get('/services/equipment-requisition-detail/1')
        self.assertEqual(resp.status_code, 200)


class ServiceViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_common_entities(cls)
        inventory.tests.models.create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )
        cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=cls.category,
            procedure=cls.procedure,
            frequency='once',
            is_listed=True
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_create_service_page(self):
        resp = self.client.get('/services/create-service')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_service_page(self):
        resp = self.client.post('/services/create-service', data={
            'name': 'name',
            'description': 'description',
            'flat_fee': 0.0,
            'hourly_rate': 1.5,
            'category': 1,
            'procedure': 1,
            'frequency': 'once',
            'is_listed': True
        })
        self.assertEqual(resp.status_code, 302)

    def test_list_services_page(self):
        resp = self.client.get('/services/list-services')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_detail_page(self):
        resp = self.client.get('/services/service-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_service_update_page(self):
        resp = self.client.get('/services/service-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_service_update_page(self):
        resp = self.client.post('/services/service-update/1', data={
            'name': 'name',
            'description': 'description',
            'hourly_rate': 1.5,
            'flat_fee': 0.0,
            'category': 1,
            'procedure': 1,
            'frequency': 'once',
            'is_listed': False
        })
        self.assertEqual(resp.status_code, 302)


class WorkOrderViewTests(TestCase):
    fixtures = ['common.json','inventory.json']

    @classmethod 
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_employees_models(cls)
        create_test_common_entities(cls)
        inventory.tests.models.create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            name="category",
            description="the description"
        )
        cls.procedure = ServiceProcedure.objects.create(
            as_checklist=True,
            name="procedure",
            reference="reference",
            description="test description"
        )
        cls.service = Service.objects.create(
            name="test service",
            description="some description",
            flat_fee=100,
            hourly_rate=10,
            category=cls.category,
            procedure=cls.procedure,
            frequency='once',
            is_listed=True
        )

        cls.wr = WorkOrderRequest.objects.create(
            service = cls.service,
            status="request",
        )
        cls.wo = ServiceWorkOrder.objects.create(
            date=str(TODAY),
            time="17:00",
            description="desc",
            status="progress",
            completed=datetime.datetime.now(),
            expected_duration=datetime.timedelta(seconds=3600),
            works_request=cls.wr
        )

        cls.sp = ServicePerson.objects.create(
            employee=cls.employee,
            is_manager = True,
            can_authorize_equipment_requisitions = False,
            can_authorize_consumables_requisitions = True
        )

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_work_order_create_page(self):
        resp = self.client.get('/services/work-order-create/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_work_order_update_page(self):
        resp = self.client.get('/services/work-order-update/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_work_order_create_page(self):
        resp = self.client.post('/services/work-order-create/1', 
            data={
                'service_people': urllib.parse.quote(json.dumps([
                    '1 - person'
                    ])),
                'date': TODAY,
                'time': '08:00:00',
                'expected_duration': '',
                'status': 'requested',
                'description': 'some description',
                'works_request': 1
            })
        self.assertEqual(resp.status_code, 302)

    def test_post_work_order_update_page(self):
        resp = self.client.post('/services/work-order-update/1', data={
            'service_people': urllib.parse.quote(json.dumps([
                    '1 - person'
                    ])),
                'date': TODAY,
                'time': '08:00:00',
                'expected_duration': '',
                'status': 'requested',
                'description': 'some description',
                'works_request': 1
                
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_work_order_detail_page(self):
        resp = self.client.get('/services/work-order-detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_work_order_detail_page(self):
        resp = self.client.get('/services/work-order-list')
        self.assertEqual(resp.status_code, 200)

    def test_get_work_order_complete_page(self):
        resp = self.client.get('/services/work-order-complete/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_work_order_complete_page(self):
        resp = self.client.post('/services/work-order-complete/1', data={
            "service_time": urllib.parse.quote(json.dumps([
                {"employee": '1 -caleb',
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "normal_time": "05:00",
                "overtime": "00:00"}
            ])), 
            "steps[]": ["1"] 
            })

        self.assertEqual(resp.status_code, 302)

    def test_work_order_authorize(self):
        self.employee.user = self.user
        self.employee.save()
        resp = self.client.post('/services/work-order-authorize/1',
            data={
                'status': 'completed',
                'authorized_by': self.employee.pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
        
    def test_get_work_order_costing_view(self):
        resp = self.client.get('/services/work-order/costing/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_work_order_expense_view(self):
        resp = self.client.get("/services/work-order/1/expense-create")
        self.assertEqual(resp.status_code, 200)


    def test_post_work_order_expense_view(self):
        resp = self.client.post("/services/work-order/1/expense-create", data={
            'description': 'description',
            'category': 1,
            'amount': 100,
            'debit_account': 1000,
            'date': datetime.date.today(),
            'recorded_by': 1
        })
        self.assertEqual(resp.status_code, 302)


class ConfigWizardTests(TestCase):
    fixtures = ['common.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(username="Testuser", email="admin@test.com", password="123")
        cls.settings = ServicesSettings.objects.create()


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_inventory_wizard(self):
        service_data = {
            '0-name': 'name',
            '0-description': 'name',
            '0-hourly_rate': 5,
            '0-flat_fee': 200,
            '0-name': 'name',
            '0-frequency': 'once',
            'config_wizard-current_step': 0
        }

        employee_data = {
            '1-first_name': 'first',
            '1-last_name': 'last',
            '1-leave_days': 1,
            '1-pin': 1000,
            'config_wizard-current_step': 1,
        }

        sp_data = {
            'config_wizard-current_step': 2,
            '2-employee': 1
        }

        data_list = [service_data, employee_data, sp_data]


        for step, data in enumerate(data_list, 1):

            try:
                resp = self.client.post(reverse('services:config-wizard'), 
                    data=data)

                if step == len(data_list):
                    self.assertEqual(resp.status_code, 302)
                else:
                    self.assertEqual(resp.status_code, 200)
                    if resp.context.get('form'):
                        if hasattr(resp.context['form'], 'errors'):
                            print(resp.context['form'].errors)
            except ValueError:
                pass


class ServiceReportsTests(TestCase):
    fixtures = ['common.json', 'inventory.json', 'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(username="Testuser", email="admin@test.com", password="123")
        cls.settings = ServicesSettings.objects.create()


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_service_person_utilization_form(self):
        resp = self.client.get(reverse(
            'services:reports-service-person-utilization-form'))
        self.assertEqual(resp.status_code, 200)

    def test_service_person_utilization_report(self):
        resp = self.client.get(reverse(
            'services:reports-service-person-utilization'), data={
                'start_period': datetime.date.today() - datetime.timedelta(days=365),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_service_person_utilization_pdf(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime("%d %B %Y"),
                'end': datetime.date.today().strftime("%d %B %Y")
            }
        req = RequestFactory().get(reverse(
            'services:reports-service-person-utilization-pdf', kwargs=kwargs)) 
        resp = ServicePersonUtilizationReportPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)

    def test_job_profitability_form(self):
        resp = self.client.get(reverse(
            'services:reports-job-profitability-form'))
        self.assertEqual(resp.status_code, 200)

    def test_job_profitability_report(self):
        resp = self.client.get(reverse(
            'services:reports-job-profitability'), data={
                'start_period': datetime.date.today() - datetime.timedelta(days=365),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_job_profitability_pdf(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime("%d %B %Y"),
                'end': datetime.date.today().strftime("%d %B %Y")
            }
        req = RequestFactory().get(reverse(
            'services:reports-job-profitability-pdf', kwargs=kwargs)) 
        resp = JobProfitabilityPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)

    def test_unbilled_costs_form(self):
        resp = self.client.get(reverse(
            'services:reports-unbilled-costs-by-job-form'))
        self.assertEqual(resp.status_code, 200)

    def test_unbilled_costs_report(self):
        resp = self.client.get(reverse(
            'services:reports-unbilled-costs-by-job'), data={
                'start_period': datetime.date.today() - datetime.timedelta(days=365),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_unbilled_costs_pdf(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime("%d %B %Y"),
                'end': datetime.date.today().strftime("%d %B %Y")
            }
        req = RequestFactory().get(reverse(
            'services:reports-unbilled-costs-by-job-pdf', kwargs=kwargs)) 
        resp = UnbilledCostsByJobPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)
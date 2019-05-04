from django.contrib.auth.models import User
from django.test import TestCase, Client 
from inventory.tests.models import create_test_inventory_models
from employees.tests.models import create_test_employees_models
from services.models import *
import urllib
import json
import datetime
from common_data.tests import create_test_common_entities


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
        create_test_inventory_models(cls)
        cls.category = ServiceCategory.objects.create(
            **{'name': 'name', 'description': 'description'}   
        )
        create_test_common_entities(cls)
        return super().setUpTestData()

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_dashboard_page(self):
        resp = self.client.get('/services/')
        self.assertEqual(resp.status_code, 302)
        # for after configuration
        settings = ServicesSettings.objects.first()
        settings.is_configured = True
        settings.save()
        resp = self.client.get('/services/')
        self.assertEqual(resp.status_code, 200)
        settings.is_configured = False
        settings.save()


    def test_get_create_category_page(self):
        resp = self.client.get('/services/create-category')
        self.assertEqual(resp.status_code, 200)

    def test_post_create_category_page(self):
        resp = self.client.post('/services/create-category',
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
        create_test_inventory_models(cls)
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
        resp = self.client.post('/services/service-person-create', 
            data={
                'employee': 1,
                'is_manager': True,
                'can_authorize_equipment_requisitions': True,
                'can_authorize_consumables_requisitions': True,
            })
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
            'members': urllib.parse.quote(json.dumps([{
                'value': '1 - Service'
            }]))
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
            'members': urllib.parse.quote(json.dumps([{
                'value': '1 - Service'
            }]))
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
        create_test_inventory_models(cls)
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
        create_test_inventory_models(cls)
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
            department="dept",
            reference="ref",
            requested_by=cls.employee
        )

        cls.con_requsition = ConsumablesRequisition.objects.create(
            date=TODAY,
            department="dept",
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
                'department': 'dept',
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
                'department': 'dept',
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
            "received_by": "Testuser",
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
        create_test_inventory_models(cls)
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
        create_test_inventory_models(cls)
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
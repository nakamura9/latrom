# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
'''
A manufacturing process has involves the transformation of 
raw materials into finished products using some process
the input is the raw materials, time, machinery and human labour
the output is finished goods. 
waste is a byproduct of a process.
the quality of the output needs to be measured
during manufacturing material location at any given moment in time must be known

when a production order is generated. the required machine(s) are reserved
time is allocated for the job and a team/shift is assigned to it.
the raw materials are reserved for the process.
The expected waste is calculated and raw materials are assigned accordingly

at each stage of the multistage process, 
output in the form of work in progress is recorded
the amount of waste generated is also recorded.
the time taken to complete the stage is also recorded.

at the end of the process the sum of all these records are 
added to the grand total for that process

the system must allow interruptions in the process to be accounted 
for and root cause analysis to be performed

time is managed as part of shifts that organize the employees working on them 
and the production schedule that is followed by the machine.

when a production order is generated the process products are evaluated and a suggested process is generated. that process is then used to update the production schedule. once a process is scheduled, its status page is updated.


he makes foam rubbers 
8 hour production
has machines 
multistage process (3)
    - preparation  cleaning machines heating chemicals 
    - mixing recipie for foam rubber 
    - forming 
    - cooling and drying 
    - cutting 
multiproduct process
waste generated
co product and by product


board making 
multistage process
    - starch preparation (batch process)
    - single facing 
    - double facing 
    - cutting and slotting 
    - work in progress 
    - printing 
    - folding and gluing 
    - strapping 
'''

class ProductionOrder(models.Model):
    date = models.DateField()
    due = models.DateField()
    customer = models.ForeignKey('invoicing.Customer', on_delete=models.SET_NULL, 
        blank=True, null=True)
    product = models.ForeignKey('inventory.InventoryItem', on_delete=models.SET_NULL, null=True)
    process = models.ForeignKey('manufacturing.Process', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.customer + ", due: " + self.due

class Process(models.Model):
 #property 
    parent_process = models.ForeignKey('manufacturing.Process', 
        on_delete=models.SET_NULL, null=True, blank=True) 
    process_equipment = models.ForeignKey('manufacturing.ProcessMachineGroup', 
        on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length = 255)
    description = models.TextField(blank=True)
    bill_of_materials = models.ForeignKey('manufacturing.BillOfMaterials', 
        on_delete=models.SET_NULL, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices = [
        (0, 'Line'),(1, 'Batch')])#line or batch
    duration = models.DurationField(blank=True, null=True) #batch
    rate = models.ForeignKey(
        'manufacturing.ProcessRate', on_delete=models.SET_NULL, null=True, blank=True)
    product_list = models.ForeignKey('manufacturing.ProductList', 
        on_delete=models.SET_NULL, null=True, blank=True)


    @property
    def process_type_string(self):
        mapping = {
            0: 'Line',
            1: 'Batch'
        }
        return mapping[self.type]

    @property
    def is_subprocess(self):
        return self.parent_process != None

    @property
    def child_processes(self):
        return Process.objects.filter(parent_process=self)

    def __str__(self):
        return self.name

class ProcessRate(models.Model):
    UNIT_TIME_CHOICES = [
            (0, 'per second'),
            (1, 'per minute'),
            (2, 'per hour'),
        ]
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    unit_time = models.PositiveSmallIntegerField(
        choices=UNIT_TIME_CHOICES
    )
    quantity = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.unit) + '/' + self.unit_time_string
        

    @property 
    def unit_time_string(self):
        mapping = dict(self.UNIT_TIME_CHOICES)
        return mapping[self.unit_time]

class ProductList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    def products(self):
        return ProcessProduct.objects.filter(product_list=self)
        

class ProcessProduct(models.Model):
    PRODUCT_TYPES = [
        (0, 'Product'),
        (1, 'By-Product'),
        (2, 'Co-Product'),
        (3, 'Waste')
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.PositiveSmallIntegerField(choices=PRODUCT_TYPES)# main product, byproduct, waste,  wip
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    finished_goods= models.BooleanField(default=False)
    inventory_product = models.ForeignKey('inventory.InventoryItem', on_delete=models.SET_NULL, null=True)
    product_list = models.ForeignKey('manufacturing.ProductList', on_delete=models.SET_NULL, 
        blank=True, 
        null=True)

    def __str__(self):
        return self.name
        
    def type_string(self):
        return dict(self.PRODUCT_TYPES)[self.type]

class WasteGenerationReport(models.Model):
    product = models.ForeignKey('manufacturing.ProcessProduct', on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()
    comments = models.TextField()
    recorded_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.product)
        
class BillOfMaterials(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
        
class BillOfMaterialsLine(models.Model):
    bill = models.ForeignKey('manufacturing.BillOfMaterials', on_delete=models.SET_NULL, null=True)
    type = models.PositiveSmallIntegerField(choices=[
        (0, 'Raw Material'),
        (1, 'Process Product')
    ]) # integer 
    raw_material = models.ForeignKey('inventory.InventoryItem', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('manufacturing.ProcessProduct', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.FloatField()
    unit =  models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        if self.raw_material is not None:
            return str(self.raw_material)
        else:
            return str(self.product)
        
    
class ProcessMachineGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models. TextField()

    def __str__(self):
        return self.name

    @property
    def machines(self):
        return ProcessMachine.objects.filter(machine_group=self)

class ProcessMachine(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_commissioned = models.DateField()
    asset_data = models.ForeignKey('accounting.Asset', on_delete=models.SET_NULL, null=True)
    machine_group = models.ForeignKey(
        'manufacturing.ProcessMachineGroup', 
        on_delete=models.SET_NULL,  
        blank=True, 
        null=True)

    def __str__(self):
        return self.name
        
'''
class MachineComponent(models.Model):
    name = 
    description = 
    component_id =
    related_spares =  
    machine = 
    parent = 
    level = 
'''

class Shift(models.Model):
    name = models.CharField(max_length =255)
    team = models.ForeignKey('services.ServiceTeam', 
        on_delete=models.SET_NULL,
        blank=True, 
        null=True)
    supervisor = models.ForeignKey('employees.Employee', 
        on_delete=models.SET_NULL, null=True,
        related_name='supervisor')
    employees = models.ManyToManyField('employees.Employee')
    machine = models.ForeignKey('manufacturing.ProcessMachine', on_delete=models.SET_NULL, null=True, default=1)


    def __str__(self):
        return self.name

        
# engineering shift, bm shift etc
class ShiftSchedule(models.Model):
    name = models.CharField(max_length=255)
    

    def __str__(self):
        return self.name

    @property
    def shifts(self):
        return ShiftScheduleLine.objects.filter(schedule=self)

class ShiftScheduleLine(models.Model):
    schedule = models.ForeignKey('manufacturing.ShiftSchedule', on_delete=models.SET_NULL, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    monday = models.BooleanField(default= True)
    tuesday = models.BooleanField(default= True)
    wednesday = models.BooleanField(default= True)
    thursday = models.BooleanField(default= True)
    friday = models.BooleanField(default= True)
    saturday = models.BooleanField(default= False)
    sunday = models.BooleanField(default= False)
    shift = models.ForeignKey('manufacturing.Shift', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return str(self.schedule) + ' ' + str(self.shift)

    

'''
====================================================
| Shift  | Start | End  | M | T | W | T | F | S | S |
====================================================
|Shift 1 | 00:00 |12:00 | x | x | x | x | x | / | / |
-----------------------------------------------------
|Shift 2 | 00:00 |12:00 | / | / | x | x | x | x | x |
-----------------------------------------------------
'''

class ManufacturingAssociate(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.employee)

class ProductionSchedule(models.Model):
    machine = models.ForeignKey('manufacturing.ProcessMachine', on_delete=models.SET_NULL, null=True)


class ProductionScheduleLine(models.Model):#rename event 
    order = models.ForeignKey('manufacturing.ProductionOrder', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()

    @property
    def shift(self):
        raise NotImplementedError()

'''Work in progress must be part of manufacturing because the it is not ordered from suppliers or sold so it does not fit in with the rest of the inventory system.'''
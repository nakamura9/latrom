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
    customer = models.ForeignKey('invoicing.Customer', on_delete=None, 
        blank=True, null=True)
    product = models.ForeignKey('inventory.Product', on_delete=None)
    process = models.ForeignKey('manufacturing.Process', on_delete=None)


class Process(models.Model):
 #property 
    parent_process = models.ForeignKey('manufacturing.Process', on_delete=None) 
    process_equipment = models.ForeignKey('manufacturing.ProcessEquipment', 
        on_delete=None)
    name = models.CharField(max_length = 255)
    description = models.TextField()
    bill_of_materials = models.ForeignKey('manufacturing.BillOfMaterials', 
        on_delete=None, blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices = [
        (0, 'Line'),(1, 'Batch')])#line or batch
    duration = models.DurationField() #batch
    rate = models.ForeignKey('manufacturing.ProcessRate', on_delete=None)
    product_list = models.ForeignKey('manufacturing.ProductList', 
        on_delete=None)

    @property
    def is_subprocess(self):
        return self.parent_process != None

class ProcessRate(models.Model):
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=None)
    unit_time = models.PositiveSmallIntegerField(
        choices=[
            (0, 'per second'),
            (0, 'per minute'),
            (0, 'per hour'),
        ]
    )
    quantity = models.FloatField()

class ProductList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

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
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=None)
    finished_goods= models.BooleanField(default=False)
    inventory_product = models.ForeignKey('inventory.Product', on_delete=None)


class WasteGenerationReport(models.Model):
    product = models.ForeignKey('manufacturing.ProcessProduct', on_delete=None)
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=None)
    quantity = models.FloatField()
    comments = models.TextField()
    recorded_by = models.ForeignKey('employees.Employee', on_delete=None)


class BillOfMaterials(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class BillOfMaterialsLine(models.Model):
    bill = models.ForeignKey('manufacturing.BillOfMaterials', on_delete=None)
    type = models.PositiveSmallIntegerField(choices=[
        (0, 'Raw Material'),
        (1, 'Process Product')
    ]) # integer 
    raw_material = models.ForeignKey('inventory.RawMaterial', on_delete=None)
    product = models.ForeignKey('manufacturing.ProcessProduct', on_delete=None)
    quantity = models.FloatField()
    unit =  models.ForeignKey('inventory.UnitOfMeasure', on_delete=None)


class ProcessEquipment(models.Model):
    machine = models.ForeignKey('manufacturing.ProcessMachine', on_delete=None)
    machine_group = models.ForeignKey('manufacturing.ProcessMachineGroup', 
        on_delete=None)
    
class ProcessMachineGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models. TextField()

class ProcessMachine(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_commissioned = models.DateField()
    asset_data = models.ForeignKey('accounting.Asset', on_delete=None)
    machine_group = models.ForeignKey(
        'manufacturing.ProcessMachineGroup', 
        on_delete=None, 
        blank=True, 
        null=True)

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
        on_delete=None, 
        blank=True, 
        null=True)
    supervisor = models.ForeignKey('employees.Employee', 
        on_delete=None,
        related_name='supervisor')
    employees = models.ManyToManyField('employees.Employee')
    process = models.ForeignKey('manufacturing.Process', on_delete=None)

# engineering shift, bm shift etc
class ShiftSchedule(models.Model):
    name = models.CharField(max_length=255)
    

class ShiftSceduleLine(models.Model):
    schedule = models.ForeignKey('manufacturing.ShiftSchedule', on_delete=None)
    start_time = models.TimeField()
    end_time = models.TimeField()
    monday = models.BooleanField(default= True)
    tuesday = models.BooleanField(default= True)
    wednesday = models.BooleanField(default= True)
    thursday = models.BooleanField(default= True)
    friday = models.BooleanField(default= True)
    Saturday = models.BooleanField(default= False)
    Sunday = models.BooleanField(default= False)
    shift = models.ForeignKey('manufacturing.Shift', on_delete=None)


class ManufacturingAssociate(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=None)


'''
====================================================
| Shift  | Start | End  | M | T | W | T | F | S | S |
====================================================
|Shift 1 | 00:00 |12:00 | x | x | x | x | x | / | / |
-----------------------------------------------------
|Shift 2 | 00:00 |12:00 | / | / | x | x | x | x | x |
-----------------------------------------------------
'''
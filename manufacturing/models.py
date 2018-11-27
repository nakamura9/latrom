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


'''


'''
class ProductionOrder(models.Model):
    date
    due 
    customer 
    product
    process 



class Process(models.Model):
    bill_of_materials
    type = #line or batch
    duration = #batch
    rate = # line process per hr

class BillOfMaterials(models.Model):
    name = 
    description = 


class BillOfMaterialsLine(models.Model):
    bill = 
    raw_material = 

#product obtained from inventory 
#raw material obtained from inventory


class ByProduct(models.Model):
    'unplanned product of a process'

class WorkInProgress(models.Model):
    pass


class CoProduct(models.Model):
    'produced along the main product and is equally important to the 
    main product'



class SubProcess(models.Model):
    machine = 
    process = 
    name = 
    description = 
    team = 
    employees = 
    raw_materials = 
    work_in_progress
    duration = #batch
    quantity = #batch


'''
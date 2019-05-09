
import random
import datetime
from decimal import Decimal as D
from functools import reduce
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from django.shortcuts import reverse

class Leave(models.Model):
    LEAVE_CATEGORIES = [
        (1, 'Annual Leave'),
        (2, 'Sick Leave'),
        (3, 'Study Leave'),
        (4, 'Maternity Leave'),
        (5, 'Parental Leave'),
        (6, 'Bereavement Leave')
    ]
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Authorized'),
        (2, 'Declined')
    ]
    start_date = models.DateField()
    end_date = models.DateField()
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, 
        related_name='employee')
    category = models.PositiveSmallIntegerField(choices=LEAVE_CATEGORIES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    authorized_by = models.ForeignKey('employees.Employee', 
            on_delete=models.SET_NULL, null=True, 
            related_name='authority', 
            limit_choices_to={'payroll_officer__isnull': False}
            )
    notes = models.TextField(blank=True)
    recorded = models.BooleanField(default=False)

    @property
    def status_string(self):
        return dict(self.STATUS_CHOICES)[self.status]

    @property
    def duration(self):
        if self.end_date == self.start_date:
            return 1 
        elif self.end_date < self.start_date:
            return 0

        return (self.end_date - self.start_date).days

    @property
    def category_string(self):
        return dict(self.LEAVE_CATEGORIES)[self.category]

    def __str__(self):
        return self.employee.__str__()

    def get_absolute_url(self):
        return reverse("employees:leave-detail", kwargs={"pk": self.pk})
    
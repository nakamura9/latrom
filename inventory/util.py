import datetime
from dateutil.relativedelta import relativedelta
import inventory
from django.db.models import Q 
from planner.models import Event, EventParticipant
from common_data.utilities import AutomatedServiceMixin

class InventoryService(AutomatedServiceMixin):
    service_name = 'inventory'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.today = datetime.date.today(*args, **kwargs)
        self.settings = inventory.models.InventorySettings.objects.first()
    
    def _run(self):
        # set an inventory check date in the calendar if the event does not yet 
        # exist and there are less than 7 days to the date
        # iterate over warehouses
        for warehouse in inventory.models.WareHouse.objects.all():
            if not warehouse.inventory_controller:
                continue
            next_check_date = None
            if not warehouse.last_inventory_check_date:
                check_month = self.today.month \
                    if self.today.day < self.settings.inventory_check_date \
                        else (self.today + relativedelta(months=1)).month
                check_year = self.today.year \
                    if self.today.day < self.settings.inventory_check_date \
                        else (self.today + relativedelta(months=1)).year
                next_check_date = datetime.date(check_year, check_month, 
                    self.settings.inventory_check_date) 
            
            else:
                if self.settings.inventory_check_frequency == 1:
                    next_check_date = warehouse.last_inventory_check_date + \
                         relativedelta(months=1)

                elif self.settings.inventory_check_frequency == 2:
                    next_check_date = warehouse.last_inventory_check_date + \
                         relativedelta(months=3)

                elif self.settings.inventory_check_frequency == 3:
                    next_check_date = warehouse.last_inventory_check_date + \
                         relativedelta(months=6)

                else:
                    next_check_date = warehouse.last_inventory_check_date + \
                         relativedelta(years=1)

            if not Event.objects.filter(Q(date=next_check_date) & 
                                        Q(label="INVENTORY_CHECK")).exists():
                Event.objects.create(date=next_check_date,
                                    reminder=datetime.timedelta(days=7),
                                    start_time="08:00:00",
                                    end_time="17:00:00",
                                    label="INVENTORY_CHECK",
                                    repeat=3,
                                    repeat_active=True,
                                    icon="file-chart-line",
                                    description=f"Event automatically generated"
                                    f"by the system. Warehouse location " 
                                    f"{warehouse.name} is scheduled to have"
                                    f"its inventory checked.",
                                    owner=warehouse.inventory_controller.employee.user)
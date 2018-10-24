from inventory.models import Order, StockAdjustment, TransferOrder


class Event(object):
    label = None
    icon = None

    def __init__(self, date):
        self.date = date
        if not self.label or self.icon:
            raise NotImplementedError('This class has no icon or label')

EVENT_MAPPING = {
    'sales': 
    'employees':
    'inventory': 
    'accounting': 
}

def get_inventory_events(date_filters):
    pass

class MonthCalendar():
    def __init__(self, request, current):
        self.request = request
        self.user = request.user
        self.current = current

    def get_event_access(self):
        if self.user
class WeekCalendar():
    pass

class DayCalendar():
    pass

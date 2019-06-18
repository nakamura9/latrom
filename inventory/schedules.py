from background_task import background
from inventory.util import InventoryService
from background_task.models import Task

@background
def run_inventory_service():
    InventoryService().run()

try:
    run_inventory_service(repeat=Task.DAILY)
except:
    # TODO handle exceptions better
    pass
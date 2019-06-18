from background_task import background
from inventory.util import InventoryService
from background_task.models import Task

@background(schedule=60)
def run_inventory_service():
    InventoryService().run()


run_inventory_service(repeat=Task.DAILY)

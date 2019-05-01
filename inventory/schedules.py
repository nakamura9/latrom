from background_task import background
from inventory.util import InventoryService

@background
def run_inventory_service():
    InventoryService().run()


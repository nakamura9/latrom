from inventory.models import InventoryItem, WareHouseItem
import datetime
import pygal

def composition_plot():
    
    stock =  InventoryItem.objects.filter(type=0)
    chart = pygal.Pie()
    chart.title = 'Inventory Composition'
    for i in stock:
        chart.add(i.name, i.quantity)

    return chart

def single_item_composition_plot(item):
    stock =  WareHouseItem.objects.filter(item=item)
    chart = pygal.Pie()
    chart.title = 'Warehouse composition'
    for i in stock:
        chart.add(str(i.warehouse), i.quantity)

    return chart
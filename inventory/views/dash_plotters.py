from inventory.models import InventoryItem, WareHouseItem
import datetime
import pygal

def stock_movement_plot():
    today = datetime.date.today()
    dates = [today- datetime.timedelta(i) for i in range(7)]
    
    dates.reverse()
    
    stock = [InventoryItem.total_inventory_quantity_on_date(i) for i in dates]
    chart = pygal.Line(fill=True)
    chart.add('Product quantity', stock)
    chart.x_labels = [i.strftime('%d/%m/%Y') for i in dates]

    return chart

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
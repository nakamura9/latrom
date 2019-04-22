from inventory.models import InventoryItem
import datetime
import pygal

def stock_movement_plot():
    today = datetime.date.today()
    dates = [today- datetime.timedelta(i) for i in range(7)]
    
    dates.reverse()
    
    stock = [InventoryItem.total_inventory_quantity_on_date(i) for i in dates]
    print(stock)
    chart = pygal.Line()
    chart.add('Product quantity', stock)
    chart.x_labels = [i.strftime('%d/%m/%Y') for i in dates]

    return chart
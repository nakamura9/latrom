import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import InventorySelectWidget from './inventory/combined_inventory_select';
import ItemReceiptTable from './inventory/stock_receipt';
import TransferItems from './inventory/transfer_order';
import InventoryChecker from './inventory/inventory_check';
import ScrappingTable from './inventory/scrapping';
import GenericTable from './src/generic_list/containers/root';

const order = document.getElementById('order-root');
const inventoryCheck =  document.getElementById('inventory-checker');
const stockReceipt =  document.getElementById('item-table');
const transferOrder = document.getElementById('transfer-items');
const scrappingApp = document.getElementById('scrapping-table');
const storageMedia = document.getElementById('id-storage-media-select');

const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
if(inventoryCheck){
    ReactDOM.render(<InventoryChecker />, inventoryCheck);
}else if(order){
    
    const isUpdate = tail !== "order-create";

    const calculateTotalFunc =(data) => {
        return parseFloat(data.order_price) * parseFloat(data.quantity)
    }

    const urlFetcher = () =>{
    
        return '/inventory/api/order/' + tail;
    }

    const resProcessor = (res) =>{
        return res.data.orderitem_set.map((item, i) =>{
            let orderItem;
            if(item.product){
                orderItem = 'P' + item.product.id + '-' + item.product.name;
            }else if(item.equipment){
                orderItem = 'E' + item.equipment.id + '-' + item.equipment.name;
            }else{//consumable
                orderItem = 'C' + item.consumable.id + '-' + item.consumable.name;
            }
            return({
                item: orderItem,
                quantity: item.quantity,
                order_price: item.order_price,
                lineTotal: item.order_price * item.quantity
            })
        })
    }

    ReactDOM.render(<GenericTable
        hasLineTotal
        hasTotal
        prepopulated={isUpdate} 
        urlFetcher={urlFetcher} 
        resProcessor={resProcessor}
        taxFormField="id_tax"
        fieldOrder={['item','unit', 'order_price', 'quantity']}
        fieldDescriptions={['Item', 'Unit', 'Order Price', 'Quantity']}
        formInputID='id_items'
        calculateTotal={calculateTotalFunc}
        fields={
            [
                {
                    name: 'item',
                    type: 'widget',
                    width: 35,
                    widgetCreator: (comp) =>{
                        return <InventorySelectWidget
                                    list={comp.props.lines}
                                    onSelect={(val) => {
                                        let newData = {...comp.state.data};
                                        newData['item'] = val;
                                        comp.setState({
                                            data: newData 
                                        })
                                    }}
                                    onClear={() =>{
                                        let newData = {...comp.state.data};
                                        newData['item'] = "";
                                        comp.setState({
                                            data: newData 
                                        })
                                    }} />;
                    }
                },
                {
                    'name': 'unit',
                    'type': 'select',
                    'width': 15,
                    'required': true,
                    'url': '/inventory/api/unit/'
                },
                {
                    'name': 'order_price',
                    'type': 'number',
                    'width': 15,
                    'required': true
                },
                {
                    'name': 'quantity',
                    'type': 'number',
                    'width': 15,
                    'required': true
                },
            
            ]
        }
        />, order);
        
        
}else if(stockReceipt){
    ReactDOM.render(<ItemReceiptTable />, stockReceipt);
}else if(transferOrder){
    ReactDOM.render(<TransferItems />, transferOrder);
}else if(scrappingApp){
    ReactDOM.render(<ScrappingTable />, scrappingApp);
}
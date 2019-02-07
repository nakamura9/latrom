import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import InventorySelectWidget from './inventory/combined_inventory_select';
import ItemReceiptTable from './inventory/stock_receipt';
import InventoryChecker from './inventory/inventory_check';
import GenericTable from './src/generic_list/containers/root';
import MutableTable from './src/mutable_table/container/root';

const order = document.getElementById('order-root');
const inventoryCheck =  document.getElementById('inventory-checker');
const stockReceipt =  document.getElementById('item-table');
const transferOrder = document.getElementById('transfer-items');
const scrappingApp = document.getElementById('scrapping-table');
const debitNoteTable = document.getElementById("debit-note-table");
const receiveTable = document.getElementById('receive-table');

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
    ReactDOM.render(<GenericTable
        fieldDescriptions={['Item', 'Quantity']}
        fieldOrder={['item', 'quantity']}
        formInputID='id_items'
        fields={[
            {
                name: 'item',
                type: 'search',
                width: 45,
                url: '/inventory/api/product/', //will get all inventory soon
                idField: 'id',
                displayField: 'name',
                required: true,
            },
            {
                name: 'quantity',
                type: 'number',
                width: 25,
                required: true
            }
        ]} />, transferOrder);
}else if(scrappingApp){
    
    ReactDOM.render(<GenericTable
        fieldDescriptions={['Item', 'Quantity', 'Note']}
        fieldOrder={['item', 'quantity', 'note']}
        formInputID='id_items'
        fields={[
            {
                name: 'item',
                type: 'search',
                width: 25,
                url: '/inventory/api/product/', //will get all inventory soon
                idField: 'id',
                displayField: 'name',
                required: true,
            },
            {
                name: 'quantity',
                type: 'number',
                width: 15,
                required: true
            },
            {
                name: 'note',
                type: 'text',
                width: 30,
                required: true
            }
        ]} />, scrappingApp);
}else if(debitNoteTable){
    ReactDOM.render(<MutableTable 
        dataURL={"/inventory/api/order/" + tail}
        headings={["Item", "Orderd Quantity", "Unit Price", "Returned Quantity"]}
        resProcessor={(res)=>{
            return res.data.orderitem_set.map((line, i) =>{
                let itemType;
                switch(line.item_type){
                    case 1:
                        itemType="product";
                        break;
                    case 2:
                        itemType="consumable";
                        break;
                    case 3:
                        itemType="equipment";
                        break;
                }
                return {
                    'item': line.id + '-' + line[itemType].name.replace('-', '_'),
                    'quantity': line.quantity,
                    'order_price': line.order_price,
                    'returned_quantity': line.returned_quantity,
                }
            })
        }}
        fields={[
            {'name': 'item', 'mutable': false},
            {'name': 'quantity', 'mutable': false},
            {'name': 'order_price', 'mutable': false},
            {'name': 'returned_quantity', 'mutable': true},
        ]}
        formHiddenFieldName="returned-items"/>, debitNoteTable)
}else if(receiveTable){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="received-items" 
            dataURL={"/inventory/api/transfer-order/" + tail}
            headings={["Item", "Quantity", "Quantity Received", "Quantity to move", "Receiving Location"]}
            resProcessor={(res) =>{
                return res.data.transferorderline_set.map((item)=>({
                    'item': item.id + ' - ' + item.product.name,
                    'quantity': item.quantity, 
                    'moved_quantity': item.moved_quantity
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'quantity', 'mutable': false},
                {'name': 'moved_quantity', 'mutable': true},
                
                
                
            ]}/>, receiveTable)

            /**
             * 'quantity_to_move': 0,
                    'receiving_location': ""
             * {'name': 'quantity_to_move', 'mutable': true},
                {'name': 'receiving_location', 'mutable': true}, */
}
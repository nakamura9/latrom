import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import GenericTable from './src/generic_list/containers/root';
import MutableTable from './src/mutable_table/container/root';
import SearchableWidget from './src/components/searchable_widget';

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
    ReactDOM.render(<MutableTable 
        formHiddenFieldName="check-table"
        dataURL={'/inventory/api/warehouse-items/' + tail}
        headings={["Item", "Recorded Quantity", "Measured Quantity"]}
        resProcessor={(res) =>{
            return res.data.results.map((item) =>{
                return {
                    item: item.id + "-" +item.item.name,
                    quantity: item.quantity,
                    measured: 0
                }
            })
        }}
        fields={[
            {name: 'item', mutable:false},
            {name: 'quantity', mutable: false},
            {name: 'measured', mutable: true}
        ]}
        />, inventoryCheck);
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
            
            return({
                item: item.item.id + '-' + item.item.name,
                quantity: item.quantity,
                unit: item.unit.id + '-' + item.unit.name,
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
                    type: 'search',
                    width: 35,
                    'model': 'inventoryitem',
                    'app': 'inventory',
                    'newLink': '/inventory/product-create',
                    url: '/inventory/api/inventory-item/', 
                    idField: 'id',
                    displayField: 'name',
                    required: true,
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
    ReactDOM.render(<MutableTable
        formHiddenFieldName="received-items" 
        dataURL={"/inventory/api/order/" + tail}
        headings={["Item", "Quantity", "Quantity Received", "Quantity to Receive", "Receiving Location"]}
        resProcessor={(res) =>{
            const itemset = res.data.orderitem_set.filter((item)=>(
                item.quantity > item.received
            ))
            return itemset.map((item)=>{
               
                return {'item': item.id + '-' + item.item.name.replace('-', '_'),
                'quantity': item.quantity, 
                'moved_quantity': item.received,
                'quantity_to_move': 0,
                'receiving_location': ""}
            })
        }}
        fields={[
            {'name': 'item', 'mutable': false},
            {'name': 'quantity', 'mutable': false},
            {'name': 'moved_quantity', 'mutable': false},
            {'name': 'quantity_to_move', 'mutable': true},
            {
                'name': 'receiving_location', 
                'mutable': true,
                'widget': true,
                'widgetCreator': (component) =>{
                    return(<SearchableWidget 
                        bordered
                        dataURL="/inventory/api/storage-media/1"
                        idField="id"
                        displayField="name"
                        onSelect={(val) => component.setState({})}
                        onClear={() =>{}}/>)
                }
            } 
            
        ]}/>, stockReceipt);
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
                url: '/inventory/api/inventory-item/', 
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
                url: '/inventory/api/inventory-item/', //will get all inventory soon
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
        headings={["Item", "Ordered Quantity", "Unit Price", "Returned Quantity"]}
        resProcessor={(res)=>{
            return res.data.orderitem_set.map((line, i) =>{
                
                return {
                    'item': line.id + '-' + line.item.name.replace('-', '_'),
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
            headings={["Item", "Ordered Quantity", "Quantity Received", "Quantity to move", "Receiving Location"]}
            resProcessor={(res) =>{
                return res.data.transferorderline_set.map((item)=>({
                    'item': item.id + ' - ' + item.item.name,
                    'quantity': item.quantity, 
                    'moved_quantity': item.moved_quantity,
                    'quantity_to_move': 0,
                    'receiving_location': ""
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'quantity', 'mutable': false},
                {'name': 'moved_quantity', 'mutable': false},
                {'name': 'quantity_to_move', 'mutable': true},
                {
                    'name': 'receiving_location', 
                    'mutable': true,
                    'widget': true,
                    'widgetCreator': (component) =>{
                        return(<SearchableWidget 
                            bordered
                            asyncDataURL={'/inventory/api/transfer-order/' + 
                                tail}
                            dataURLResProcessor={(res) =>{
                                return '/inventory/api/storage-media/' + res.data.receiving_warehouse
                            }}
                            idField="id"
                            displayField="name"
                            onSelect={(val) => component.setState({})}
                            onClear={() =>{}}/>)
                    }
                } 
                
            ]}/>, receiveTable)
}
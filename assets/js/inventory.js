import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import GenericTable from './src/generic_list/containers/root';
import MutableTable from './src/mutable_table/container/root';
import SearchableWidget from './src/components/searchable_widget';

const order = document.getElementById('order-root');
const inventoryCheck =  document.getElementById('inventory-checker');
const orderReceipt =  document.getElementById('order-receipt-table');
const returnsReceipt =  document.getElementById('returns-receipt-table');
const transferReceipt =  document.getElementById('transfer-receipt-table');
const transferOrder = document.getElementById('transfer-items');
const scrappingApp = document.getElementById('scrapping-table');
const debitNoteTable = document.getElementById("debit-note-table");
const debitNoteDispatch = document.getElementById('debit-note-dispatch');
const salesDispatch = document.getElementById('sales-dispatch');

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
}else if(transferReceipt){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="received-items" 
            dataURL={"/inventory/api/transfer-order/" + tail}
            headings={["Item", "Ordered Quantity", "Quantity Received", "Quantity to move", "Receiving Location"]}
            resProcessor={(res) =>{
                let lines = res.data.transferorderline_set.filter((item) =>{
                    return item.quantity > item.moved_quantity
                })
                return lines.map((item)=>({
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
                
            ]}/>, transferReceipt)
}else if(orderReceipt){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="received-items" 
            dataURL={"/inventory/api/order/" + tail}
            headings={["Item", "Ordered Quantity", "Quantity Received",  "Receiving Location"]}
            resProcessor={(res) =>{
                return res.data.orderitem_set.map((item)=>({
                    'item': item.id + ' - ' + item.item.name,
                    'quantity': item.quantity, 
                    'receiving_location': ""
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'quantity', 'mutable': false},
                {'name': 'quantity_received', 'mutable': true},
                {
                    'name': 'receiving_location', 
                    'mutable': true,
                    'widget': true,
                    'widgetCreator': (component) =>{
                        return(<SearchableWidget 
                            bordered
                            asyncDataURL={'/inventory/api/order/' + 
                                tail}
                            dataURLResProcessor={(res) =>{
                                return '/inventory/api/storage-media/' + res.data.ship_to
                            }}
                            idField="id"
                            displayField="name"
                            onSelect={(val) => component.setState({})}
                            onClear={() =>{}}/>)
                    }
                } 
                
            ]}/>, orderReceipt)
}else if(returnsReceipt){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="received-items" 
            dataURL={"/invoicing/api/credit-note/" + tail}
            headings={["Item", "Ordered Quantity", "Quantity To Return", "Quantity", "Receiving Location"]}
            resProcessor={(res) =>{
                let lines = res.data.creditnoteline_set.filter(item =>{
                    // removes services and expenses
                    return item.line.product !== null && item.quantity > item.line.product.returned_quantity 
                })
                return lines.map((item)=>({
                    'item': item.name,
                    'ordered_quantity': item.line.product.quantity, 
                    'return_quantity': item.quantity,
                    'quantity': 0,
                    'receiving_location': "",
                    'id': item.id
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'ordered_quantity', 'mutable': false},
                {'name': 'return_quantity', 'mutable': false},
                {'name': 'quantity', 'mutable': true},
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
                
            ]}/>, returnsReceipt)
}else if(debitNoteDispatch){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="sent-items" 
            dataURL={"/inventory/api/debit-note/" + tail}
            headings={["Item", "Ordered Quantity", "Quantity To Return", "Quantity"]}
            resProcessor={(res) =>{

                let lines = res.data.debitnoteline_set
                return lines.map((item)=>({
                    'item': item.id + '-' + item.item.item.name,
                    'ordered_quantity': item.item.quantity, 
                    'return_quantity': item.quantity,
                    'quantity': 0,
                    'id': item.id
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'ordered_quantity', 'mutable': false},
                {'name': 'return_quantity', 'mutable': false},
                {'name': 'quantity', 'mutable': true},
                
            ]}/>, debitNoteDispatch)
}else if(salesDispatch){
    ReactDOM.render(<MutableTable
            formHiddenFieldName="sent-items" 
            dataURL={"/invoicing/api/invoice/" + tail}
            headings={["Item", "Invoiced Quantity",  "Quantity Dispatched"]}
            resProcessor={(res) =>{

                let lines = res.data.invoiceline_set.filter((line) =>{
                    return line.product !== null;
                })
                return lines.map((item)=>({
                    'item': item.id + '-' + item.product.product.name,
                    'invoiced_quantity': item.product.quantity, 
                    'quantity': 0,
                    'id': item.id
                }))
            }}
            fields={[
                {'name': 'item', 'mutable': false},
                {'name': 'invoiced_quantity', 'mutable': false},
                {'name': 'quantity', 'mutable': true},
                
            ]}/>, salesDispatch)
}
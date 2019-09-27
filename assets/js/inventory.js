import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import GenericTable from './src/generic_list/containers/root';
import MutableTable from './src/mutable_table/container/root';
import SearchableWidget from './src/components/searchable_widget';
import SelectWidget from './src/components/select';


const order = document.getElementById('order-root');
const inventoryCheck =  document.getElementById('inventory-checker');
const stockReceipt =  document.getElementById('item-table');
const transferOrder = document.getElementById('transfer-items');
const scrappingApp = document.getElementById('scrapping-table');
const debitNoteTable = document.getElementById("debit-note-table");
const receiveTable = document.getElementById('receive-table');
const purchaseTable = document.getElementById('purchase-table');
const multipleItemsTable = document.getElementById('multiple-item-list');
const multipleSuppliersTable = document.getElementById('multiple-suppliers-list');


const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
const wh = decomposed[decomposed.length - 2];


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
                    url: '/inventory/api/product/', 
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
                'widgetCreator': (comp, rowID) =>{

                    const handler = (val) =>{
                        let newData = [...comp.state.data];
                        let newRow = {...comp.state.data[rowID]};
                        newRow['receiving_location'] = val;
                        newData[rowID] = newRow;
                        comp.setState({'data': newData}, comp.updateForm)
                    }

                    const clearHandler = () =>{
                        let newData = [...comp.state.data];
                        let newRow = {...comp.state.data[rowID]};
                        newRow['receiving_location'] = '';
                        newData[rowID] = newRow;
                        comp.setState({'data': newData}, comp.updateForm)
                    }

                    
                    return(<SearchableWidget 
                        bordered
                        dataURL={`/inventory/api/storage-media/${wh}`}
                        idField="id"
                        displayField="name"
                        onSelect={handler}
                        onClear={clearHandler}/>)
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
            headings={["Item", "Quantity", "Quantity Received", "Quantity to move", "Receiving Location"]}
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
                    'widgetCreator': (comp, rowID) =>{
                        const handler = (val) =>{
                            let newData = [...comp.state.data];
                            let newRow = {...comp.state.data[rowID]};
                            newRow['receiving_location'] = val;
                            newData[rowID] = newRow;
                            comp.setState({'data': newData}, comp.updateForm)
                        }
    
                        const clearHandler = () =>{
                            let newData = [...comp.state.data];
                            let newRow = {...comp.state.data[rowID]};
                            newRow['receiving_location'] = '';
                            newData[rowID] = newRow;
                            comp.setState({'data': newData}, comp.updateForm)
                        }
                        return(<SearchableWidget 
                            bordered
                            dataURL={`/inventory/api/storage-media/${wh}`}
                            idField="id"
                            displayField="name"
                            onSelect={handler}
                            onClear={clearHandler}/>)
                    }
                } 
                
            ]}/>, receiveTable)
}else if(multipleItemsTable){
    ReactDOM.render(<GenericTable 
        fieldOrder={['name', 'type', 'purchase_price', 'sales_price', 'quantity', 'unit']}
        fieldDescriptions={['Name', 'Type', 'Purchase Price', 'Sales Price','Quantity', 
            'Unit']}
        formInputID='id_data'
        fields={[
            {
                'name': 'name',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'type',
                'type': 'widget',
                'width': '15',
                'required': true,
                'widgetCreator': (comp) =>{
                    const handler = (value) =>{
                        let newData = {...comp.state.data}
                        newData['type'] = value
                        comp.setState({'data': newData})
                    }
                    return(
                        <SelectWidget
                            
                            handler={handler}
                            resetFlag={comp.state.isReset}
                            options={[
                                {
                                    'label': 'Product',
                                    'value': 0
                                },
                                {
                                    'label': 'Equipment',
                                    'value': 1                                },
                                {
                                    'label': 'Consumable',
                                    'value': 2
                                }
                            ]} />
                    )
                }
            },
            {
                'name': 'purchase_price',
                'type': 'number',
                'width': '10',
                'required': true
            },
            {
                'name': 'sales_price',
                'type': 'number',
                'width': '10',
                'required': true
            },
            {
                'name': 'quantity',
                'type': 'number',
                'width': '10',
                'required': true
            },
            
            {
                'name': 'unit',
                'type': 'text',
                'width': '10',
                'required': true,

                }
        ]}
            />, multipleItemsTable)
}else if(multipleSuppliersTable){
    ReactDOM.render(<GenericTable 
        fieldOrder={['name', 'address', 'email', 'phone', 'account_balance']}
        fieldDescriptions={['Name', 'Address', 'Email', 'Phone',
            'Account Balance']}
        formInputID='id_data'
        fields={[
            {
                'name': 'name',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'address',
                'type': 'text',
                'width': '30',
                'required': true
            },
            {
                'name': 'email',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'phone',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'account_balance',
                'type': 'number',
                'width': '15',
                'required': true,
            }
        ]}
            />, multipleSuppliersTable)
}else if(purchaseTable){

    const calculateTotalFunc =(data) => {
        return parseFloat(data.unit_price) * parseFloat(data.quantity)
    }

    

    ReactDOM.render(<GenericTable
        
        hasLineTotal
        hasTotal
        fieldOrder={['item','unit', 'unit_price', 'quantity']}
        fieldDescriptions={['Item', 'Unit', 'Unit Price', 'Quantity']}
        formInputID='id_data'
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
                    url: '/inventory/api/items-excluding-products/', 
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
                    'name': 'unit_price',
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
        />, purchaseTable);
        
        
}
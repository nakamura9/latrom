import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import Invoice from './invoices/invoice';
import MutableTable from './src/mutable_table/container/root';
import SelectWidget from './src/components/select';
import GenericTable from './src/generic_list/containers/root';

const creditNote = document.getElementById('credit-note-table');
const directPurchase =  document.getElementById('direct-purchase-table');
const sales = document.getElementById('invoice-table');
const multipleCustomersTable = document.getElementById('multiple-customers-list');

const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
    
if(sales){
    ReactDOM.render(<Invoice />, sales);
}else if(creditNote){
    let decomposedURL = window.location.href.split('/');
    let pk = decomposedURL[decomposedURL.length - 1];
    ReactDOM.render(<MutableTable 
        dataURL={'/invoicing/api/invoice/' + pk}
        headings={["Product", "Invoiced Quantity", "Unit Price", "Returned Quantity"]}
        resProcessor={(res) =>{
            // filter by lines which have a returned value less than 1
            const filtered = res.data.invoiceline_set.filter((line) => line.product)
            return filtered.map((line, i)=>({
                product: line.id + " - " +line.product.product.name,
                quantity: line.product.quantity,
                unit_price: line.product.unit_price,
                returned_quantity: line.product.returned_quantity
            }))
        }}
        fields={[
            {'name': 'product', 'mutable': false},
            {'name': 'quantity', 'mutable': false},
            {'name': 'unit_price', 'mutable': false},
            {'name': 'returned_quantity', 'mutable': true},
        ]}
        formHiddenFieldName="returned-items"
        />, creditNote)
}else if(directPurchase){
    ReactDOM.render(<PurchaseTable />, directPurchase);
}else if(multipleCustomersTable){
    ReactDOM.render(<GenericTable 
        fieldOrder={['name','type', 'address', 'email', 'phone', 'account_balance']}
        fieldDescriptions={['Name','Type', 'Address', 'Email', 'Phone',
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
                'name': 'type',
                'type': 'widget',
                'width': '10',
                'required': true,
                'widgetCreator': (comp) =>{
                    const handler = (value) =>{
                        let newData = {...comp.state.data}
                        newData['type'] = value
                        comp.setState({'data': newData})
                    }
                    return(
                        <SelectWidget
                            resetFlag={comp.state.isReset}
                            handler={handler}
                            options={[
                                {
                                    'value': 'organization',
                                    'label': 'Organization'
                                },
                                {
                                    'label': 'individual',
                                    'value': 'Individual'
                                },
                               
                            ]} />
                    )
                }
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
            />, multipleCustomersTable);
}
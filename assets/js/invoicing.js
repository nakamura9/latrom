import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import axios from 'axios';
import SalesInvoiceForm from './invoices/sales_invoice';
import BillTable from './invoices/bill';
import ServiceLineTable from './invoices/service_invoice';
import CreditNoteTable from './invoices/credit_note';
import CombinedTable from './invoices/combined_invoice';
import GenericTable from './src/generic_list/containers/root';

const sales = document.getElementById('sales-invoice-contents');
const bill = document.getElementById('bill-contents');
const services = document.getElementById('service-invoice-contents');
const creditNote = document.getElementById('credit-note-table');
const directPurchase =  document.getElementById('direct-purchase-table');
const combinedInvoce = document.getElementById('combined-invoice-contents');


if(sales){
    const calculateTotalFunc = (data)=>{
        return(data.quantity * data.unit_price);
    }
    const priceGetter = (comp, fieldName, pk) =>{
        axios({
            url: '/inventory/api/product/' + pk,
            method:'get'
        }).then(res => {
            let newData = {...comp.state.data};
            newData[fieldName] = parseFloat(res.data.unit_sales_price)
                                        .toFixed(2);
            comp.setState({data: newData});
        });
    }
    const URL = window.location.href;
    const  decomposed = URL.split('/');
    const tail = decomposed[decomposed.length - 1];
    
    const isUpdate = tail !== 'create-sales-invoice';
    
    const urlFetcher = () =>{
        const URL = window.location.href;
        const  decomposed = URL.split('/');
        const tail = decomposed[decomposed.length - 1];
    
        return '/invoicing/api/sales-invoice/' + tail;
    }
    
    const resProcessor = (res) =>{
        return res.data.salesinvoiceline_set.map((line) =>(
            {
                product: line.product.id + '-' + line.product.name,
                unit_price: line.product.unit_sales_price,
                quantity: line.quantity,
                lineTotal: parseFloat(line.quantity) * 
                            parseFloat(line.product.unit_sales_price)
            }
        ))
        }
              
    console.log(isUpdate);
            
    ReactDOM.render(<GenericTable hasLineTotal={true}
        hasTotal={true}
        prepopulated={isUpdate}
        resProcessor={resProcessor}
        urlFetcher={urlFetcher}
        taxFormField="id_tax"
        calculateTotal={calculateTotalFunc}
        fieldDescriptions={['Product', 'Unit Price', 'Quantity']} 
        fieldOrder={['product', 'unit_price','quantity']}
        formInputID={'id-item-list'}
        fields={[
            {
                name: 'product',
                type: 'search',
                width: 40,
                required: true,
                url: '/inventory/api/product/',
                idField: 'id',
                canCreateNewItem: true,
                newLink: '/inventory/product-create',
                displayField: 'name'
            },
            {
                name: 'unit_price',
                type: 'fetch',
                width: 15,
                required: true,
                dataGetter: priceGetter

            },
            {
                name: 'quantity',
                type: 'number',
                width: 15,
                required: true
            },
        ]}/>, sales);

}else if(bill){
    ReactDOM.render(<BillTable />, bill);
}else if(services){
    ReactDOM.render(<ServiceLineTable />, services);
}else if(creditNote){
    ReactDOM.render(<CreditNoteTable />, creditNote)
}else if(directPurchase){
    ReactDOM.render(<PurchaseTable />, directPurchase);
}else if(combinedInvoce){
    ReactDOM.render(<CombinedTable />, combinedInvoce);
}

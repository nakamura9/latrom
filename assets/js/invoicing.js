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

const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
    

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
    
    const isUpdate = tail !== 'create-sales-invoice';
    
    const urlFetcher = () =>{
    
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
    
    const isUpdate = tail !== 'create-service-invoice';

    const urlFetcher = () =>{  
        return '/invoicing/api/service-invoice/' + tail;
    }

    const calculateTotalFunc = (data)=>{
        console.log(data);
        return(parseFloat(data.fixed_fee) + (
            parseFloat(data.rate) * parseFloat(
                data.hours)));
    }

    const rateGetter = (comp, fieldName, pk) =>{
        axios({
            url: '/services/api/service/' + pk,
            method:'get'
        }).then(res => {
            console.log(res.data);
            let newData = {...comp.state.data};
            newData[fieldName] = parseFloat(res.data.hourly_rate)
                                        .toFixed(2);
            newData['fixed_fee'] = parseFloat(res.data.flat_fee)
                                        .toFixed(2);
            comp.setState({data: newData});
        });
    }

    const fixedFeeGetter = (comp, fieldName, pk) =>{
        return;
        //actual data set in rate getter to avoid hitting the server twice
    }

    const resProcessor = (res) =>{
        return res.data.serviceinvoiceline_set.map((line) =>(
            {
                service: line.service.id + '-' + line.service.name,
                rate: line.service.hourly_rate,
                hours: line.hours,
                fixed_fee: line.service.flat_fee,
                lineTotal: (parseFloat(
                    line.service.hourly_rate) * parseFloat(line.hours)) + parseFloat(line.service.flat_fee)
            }
        ))
        }
    

    ReactDOM.render(<GenericTable
        hasTotal
        hasLineTotal
        prepopulated={isUpdate}
        resProcessor={resProcessor}
        urlFetcher={urlFetcher}
        taxFormField="id_tax"
        calculateTotal={calculateTotalFunc}
        fieldDescriptions={['Service','Fixed Fee', 'Hourly Rate', 'Hours']} 
        fieldOrder={['service', 'fixed_fee', 'rate','hours']}
        formInputID={'id-item-list'}
        fields={[{
            'name': 'service',
            'type': 'search',
            'width': 35,
            'required': true,
            'url': '/services/api/service/',
            'idField': 'id',
            'canCreateNewItem': true,
            'newLink': '/services/create-service',
            'displayField': 'name'
        }, 
        {
            'name': 'fixed_fee',
            'type': 'fetch',
            'width': 10,
            required: true,
            dataGetter: fixedFeeGetter
        }, 
        {
            'name': 'rate',
            'type': 'fetch',
            'width': 10,
            required: true,
            dataGetter: rateGetter
        }, {
            'name': 'hours',
            'type': 'number',
            'width': 15,
            'required': true
        }]}
         />, services);

}else if(creditNote){
    ReactDOM.render(<CreditNoteTable />, creditNote)
}else if(directPurchase){
    ReactDOM.render(<PurchaseTable />, directPurchase);
}else if(combinedInvoce){
    ReactDOM.render(<CombinedTable />, combinedInvoce);
}

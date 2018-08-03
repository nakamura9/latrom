import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import SalesInvoiceForm from './invoices/sales_invoice';
import BillTable from './invoices/bill';
import ServiceLineTable from './invoices/service_invoice';
import CreditNoteTable from './invoices/credit_note';
import CombinedTable from './invoices/combined_invoice';

const sales = document.getElementById('sales-invoice-contents');
const bill = document.getElementById('bill-contents');
const services = document.getElementById('service-invoice-contents');
const creditNote = document.getElementById('credit-note-table');
const directPurchase =  document.getElementById('direct-purchase-table');
const combinedInvoce = document.getElementById('combined-invoice-contents');


if(sales){
    ReactDOM.render(<SalesInvoiceForm />, sales);
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

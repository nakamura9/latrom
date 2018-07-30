import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import InvoiceTable from './invoices/simple_invoice_table';
import SalesInvoiceForm from './invoices/sales_invoice';
import BillTable from './invoices/bill';
import ServiceLineTable from './invoices/service_invoice';
import CreditNoteTable from './invoices/credit_note';
import CombinedTable from './invoices/combined_invoice';

function addHandler(item, count){
    $("<input>")
            .attr({
                "type": "hidden",
                "name": "items[]",
                "id": "item_" + item.code,
                "value":encodeURIComponent(JSON.stringify({
                    'code': item.code,
                    'quantity': item.quantity,
                    'discount': item.discount
                })) 
                }).appendTo("form");
}

function removeHandler(id){
    // used to remove hidden inputs from the form
    $("#item_" + id).remove();
}

function populatedRemoveHandler(code){
    // used in update views to remove existing items
    $("<input>")
            .attr({
                "type": "hidden",
                "name": "removed_items[]",
                "id": "removed_item_" + code,
                "value": code
                }).appendTo("form");
}

function searchHandler(data){
    var decomposed = data.split('-');
    $("#id_customer").val(decomposed[0]);
}

function populatedHandler(widget){
    var urlElements = window.location.href.split("/");
    var invNo = urlElements[urlElements.length- 1]; 
    $.ajax({
        url: "/invoicing/api/invoice/" + invNo + "/",
        data: {},
        method: "GET"
    }).then(res => {
        widget.setState({
            selected: true,
            inputVal: res.customer.id + " - " +                             res.customer.first_name + 
                " " + res.customer.last_name
        });
    });
}

const populated = document.getElementById('populated-item-table');
const inv = document.getElementById('item-table');
const sales = document.getElementById('sales-invoice-contents');
const bill = document.getElementById('bill-contents');
const services = document.getElementById('service-invoice-contents');
const creditNote = document.getElementById('credit-note-table');
const directPurchase =  document.getElementById('direct-purchase-table');
const combinedInvoce = document.getElementById('combined-invoice-contents');

if(populated){
    ReactDOM.render(<InvoiceTable 
        populated={true} 
        populatedRemoveHandler={populatedRemoveHandler} 
        addHandler={addHandler} 
        removeHandler={removeHandler}
        url="/invoicing/api/invoice/" />, 
        document.getElementById('populated-item-table'));
}else if(inv){
    
    ReactDOM.render(<InvoiceTable populated={false} 
        addHandler={addHandler} 
        removeHandler={removeHandler}
        url="/invoicing/api/invoice/" />, inv);
}else if(sales){
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
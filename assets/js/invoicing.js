import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import InvoiceTable from './src/invoice_table';
import SearchWidget from './src/search_widget';
import $ from 'jquery';

var populated = document.getElementById('populated-item-table');

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

if(populated){
    ReactDOM.render(<InvoiceTable 
        populated={true} 
        populatedRemoveHandler={populatedRemoveHandler} 
        addHandler={addHandler} 
        removeHandler={removeHandler}
        url="/invoicing/api/invoice/" />, 
        document.getElementById('populated-item-table'));
    /*
    ReactDOM.render(<SearchWidget populated={true} 
        populatedHandler={populatedHandler} 
        url="/invoicing/api/customer/" 
        handler={searchHandler} />, 
        document.getElementById('customer-search')); */
}else{
    ReactDOM.render(<InvoiceTable populated={false} 
        addHandler={addHandler} 
        removeHandler={removeHandler}
        url="/invoicing/api/invoice/" />, document.getElementById('item-table'));
    /**
    ReactDOM.render(<SearchWidget  url="/invoicing/api/customer/" 
        handler={searchHandler} />, 
        document.getElementById('customer-search')); */
}

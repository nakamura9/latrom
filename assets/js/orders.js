import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import OrderTable from './src/order_table';
import SearchWidget from './src/search_widget';
import $ from 'jquery';

var populated = document.getElementById("populated-root");
var fields = ['Item Name', 'Description', 'Quantity', 'Order Price', 'Unit', 'Subtotal'];
if(populated){
    ReactDOM.render(<OrderTable populated={true} fields={fields} />, populated);
}else{
    ReactDOM.render(<OrderTable populated={false} fields={fields} />, document.getElementById('root'));
}

    
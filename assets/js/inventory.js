import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import OrderTable from './inventory/orders';
import ItemReceiptTable from './inventory/stock_receipt';
import TransferItems from './inventory/transfer_order';
import InventoryChecker from './inventory/inventory_check';

const orderFields = ['Item', 'Quantity', 'Order Price','Subtotal'];
const newOrder = document.getElementById('root');
const updatedOrder = document.getElementById("populated-root"); 
const inventoryCheck =  document.getElementById('inventory-checker');
const stockReceipt =  document.getElementById('item-table');
const transferOrder = document.getElementById('transfer-items');

if(inventoryCheck){
    ReactDOM.render(<InventoryChecker />, inventoryCheck);
}else if(newOrder){
    ReactDOM.render(<OrderTable populated={false} fields={orderFields} />, newOrder);
}else if(updatedOrder){
    ReactDOM.render(<OrderTable populated={true} fields={orderFields} />, updatedOrder);
}else if(stockReceipt){
    ReactDOM.render(<ItemReceiptTable />, stockReceipt);
}else if(transferOrder){
    ReactDOM.render(<TransferItems />, transferOrder);
}
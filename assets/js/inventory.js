import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import OrderTable from './inventory/orders';
import ItemReceiptTable from './inventory/stock_receipt';
import TransferItems from './inventory/transfer_order';
import InventoryChecker from './inventory/inventory_check';
import ScrappingTable from './inventory/scrapping';
import GenericTable from './src/generic_list/containers/root';

const orderFields = ['Item', 'Quantity', 'Order Price','Subtotal'];
//const order = document.getElementById('order-root');
const inventoryCheck =  document.getElementById('inventory-checker');
const stockReceipt =  document.getElementById('item-table');
const transferOrder = document.getElementById('transfer-items');
const scrappingApp = document.getElementById('scrapping-table');
const storageMedia = document.getElementById('id-storage-media-select');
/*
const URL = window.location.href;
const  decomposed = URL.split('/');
const tail = decomposed[decomposed.length - 1];
*/
if(inventoryCheck){
    ReactDOM.render(<InventoryChecker />, inventoryCheck);
}/*else if(order){

    const isUpdate = tail !== "order-create";
    ReactDOM.render(<GenericTable
        hasLineTotal
        hasTotal
        prepopulated={isUpdate}
        taxFormField="id_tax"
        fields={[
            {'product'}
        ]}
        />, order);
        
        
}*/else if(stockReceipt){
    ReactDOM.render(<ItemReceiptTable />, stockReceipt);
}else if(transferOrder){
    ReactDOM.render(<TransferItems />, transferOrder);
}else if(scrappingApp){
    ReactDOM.render(<ScrappingTable />, scrappingApp);
}
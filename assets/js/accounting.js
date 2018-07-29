import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TransactionTable from './accounting/compound_transaction';


const transactionTable = document.getElementById('transaction-table');
if(transactionTable){
    ReactDOM.render(<TransactionTable />, transactionTable)
}


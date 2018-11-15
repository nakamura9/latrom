import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TransactionTable from './accounting/compound_transaction';
import CurrencyConverter from './accounting/currency/containers/root';

const transactionTable = document.getElementById('transaction-table');
const currency = document.getElementById('currency-converter');
console.log(currency);
if(transactionTable){
    ReactDOM.render(<TransactionTable />, transactionTable);
}else if(currency){
    ReactDOM.render(<CurrencyConverter />, currency);
}


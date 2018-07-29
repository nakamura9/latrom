import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import Payroll from './employees/payroll';
import TaxBracketTable from './employees/tax_brackets';

const payroll = document.getElementById('payroll-table');
const taxTable = document.getElementById('tax-brackets');
if(payroll){
    ReactDOM.render(<Payroll />, payroll);
}else if(taxTable){
    ReactDOM.render(<TaxBracketTable />, taxTable);
}

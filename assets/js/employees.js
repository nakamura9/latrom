import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import Payroll from './employees/payroll';
import TaxBracketTable from './employees/tax_brackets';
import TimeSheet from './employees/timesheet';

const payroll = document.getElementById('payroll-table');
const taxTable = document.getElementById('tax-brackets');
const timeSheet = document.getElementById('timesheet-root');
if(payroll){
    ReactDOM.render(<Payroll />, payroll);
}else if(taxTable){
    ReactDOM.render(<TaxBracketTable />, taxTable);
}else if(timeSheet){
    ReactDOM.render(<TimeSheet />, timeSheet);
}

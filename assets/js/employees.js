import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import Payroll from './employees/payroll';
import TaxBracketTable from './employees/tax_brackets';
import TimeSheet from './employees/timesheet/container/root';
import LeaveCalendar from './employees/leave/container/root';

const payroll = document.getElementById('payroll-table');
const taxTable = document.getElementById('tax-brackets');
const timeSheet = document.getElementById('timesheet-root');
const leaveCalendarContainer = document.getElementById('leave-calendar');

if(payroll){
    ReactDOM.render(<Payroll />, payroll);
}else if(taxTable){
    ReactDOM.render(<TaxBracketTable />, taxTable);
}else if(timeSheet){
    ReactDOM.render(<TimeSheet />, timeSheet);
}else if(leaveCalendarContainer){
    ReactDOM.render(<LeaveCalendar />, leaveCalendarContainer)
}

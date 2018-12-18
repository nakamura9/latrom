import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import TimeSheet from './employees/timesheet/container/root';
import LeaveCalendar from './employees/leave/container/root';
import GenericTable from './src/generic_list/containers/root';

const taxTable = document.getElementById('tax-brackets');
const timeSheet = document.getElementById('timesheet-root');
const leaveCalendarContainer = document.getElementById('leave-calendar');

if(taxTable){
    ReactDOM.render(<GenericTable
        fieldDescriptions={['Lower Limit', 'Upper Limit', 'Rate(%)', 'Deduction']}
        fieldOrder={['lower_limit', 'upper_limit', 'rate', 'deduction']}
        formInputID='id_brackets'
        fields={[
            {
                name: 'lower_limit',
                type: 'number',
                width: 15,
                required: true,
            },
            {
                name: 'upper_limit',
                type: 'number',
                width: 15,
                required: true
            },
            {
                name: 'rate',
                type: 'number',
                width: 15,
                required: true
            },
            {
                name: 'deduction',
                type: 'number',
                width: 15,
                required: true
            }
        ]} />, taxTable);
}else if(timeSheet){
    ReactDOM.render(<TimeSheet />, timeSheet);
}else if(leaveCalendarContainer){
    ReactDOM.render(<LeaveCalendar />, leaveCalendarContainer)
}

import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import TimeSheet from './employees/timesheet/container/root';
import LeaveCalendar from './employees/leave/container/root';
import GenericTable from './src/generic_list/containers/root';

const taxTable = document.getElementById('tax-brackets');
const timeSheet = document.getElementById('timesheet-root');
const leaveCalendarContainer = document.getElementById('leave-calendar');
const employeesList = document.getElementById('multiple-employees-list');

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
}else if(employeesList){
    ReactDOM.render(<GenericTable 
        fieldOrder={['first_name','last_name', 'address', 'email', 'phone', 'date_of_birth']}
        fieldDescriptions={['First name','Last name', 'Address', 'Email', 'Phone','Date of Birth']}
        formInputID='id_data'
        fields={[
            {
                'name': 'first_name',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'last_name',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'address',
                'type': 'text',
                'width': '30',
                'required': true
            },
            {
                'name': 'email',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'phone',
                'type': 'text',
                'width': '15',
                'required': true
            },
            {
                'name': 'date_of_birth',
                'type': 'date',
                'width': '15',
                'required': true,
            }
        ]}/>, employeesList)
}

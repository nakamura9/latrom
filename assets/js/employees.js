import React, {Component} from 'react';
import ReactDOM from 'react-dom';

import TimeSheet from './employees/timesheet/container/root';
import LeaveCalendar from './employees/leave/container/root';
import GenericTable from './src/generic_list/containers/root';
import MutableTable from './src/mutable_table/container/root';
import SelectWidget from './src/components/select';


const taxTable = document.getElementById('tax-brackets');
const timeSheet = document.getElementById('timesheet-root');
const leaveCalendarContainer = document.getElementById('leave-calendar');
const employeesList = document.getElementById('multiple-employees-list');
const outstandingSlips = document.getElementById('outstanding-payslips');
console.log(outstandingSlips);

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
}else if(outstandingSlips){
    ReactDOM.render(<MutableTable 
            dataURL='/employees/api/outstanding-payslips/'
            formHiddenFieldName='data'
            resProcessor={(res) =>{
                return res.data.map((i) =>({
                    'id': i.id,
                    'employee': `${i.employee.last_name}, ${i.employee.first_name}`, 
                    'gross': i.gross.toFixed(2), 
                    'deductions': i.deductions.toFixed(2),
                    'taxes': i.taxes.toFixed(2),
                    'current': i.status,
                    'status': i.status,
                    'period': `${i.end_period} to ${i.start_period}` 
                }))
            }}
            headings={['#', 'Employee', 'Period', 'Gross', 'Deductions', 'Taxes', 'Current Status','New Status']}
            fields={[
                {'name': 'id', 'mutable': false},
                {'name': 'employee', 'mutable': false},
                {'name': 'period', 'mutable': false},
                {'name': 'gross', 'mutable': false},
                {'name': 'deductions', 'mutable': false},
                {'name': 'taxes', 'mutable': false},
                {'name': 'current', 'mutable': false},
                {'name': 'status', 'mutable': true, 'widget': true,
                    'widgetCreator': (comp, rowID) =>{

                        const handler = (val) =>{
                            let newData = [...comp.state.data];
                            let newRow = {...comp.state.data[rowID]};
                            newRow['status'] = val;
                            newData[rowID] = newRow;
                            comp.setState({'data': newData}, comp.updateForm)
                        }
                        return <SelectWidget
                                    handler={handler}
                                    options={[
                                        {
                                            'label': 'Verified',
                                            'value': "verified"
                                        },
                                        {
                                            'label': 'Paid',
                                            'value': "paid"
                                        }
                                    ]}
                                    />

                    }},
            ]}

            
            />, outstandingSlips)
}

import React from 'react';
import ReactDOM from 'react-dom';
import {ProcedureViews, InventorySelectWidgets} from '../js/services/procedure';
import MultipleSelectWidget from '../js/src/multiple_select/containers/root';
import GenericTable from './src/generic_list/containers/root';
import TimeField from './src/components/time_field';
import NotesWidget from './src/notes_widget/root';

const procedure = document.getElementById('procedure-widgets');
const inventory = document.getElementById('inventory-widgets');
const personnel = document.getElementById('personnel-list');
const consumableTable = document.getElementById('consumable-requisition-table');
const equipmentTable = document.getElementById('equipment-requisition-table');
const workOrderPersons = document.getElementById('work-order-persons');
const serviceTime = document.getElementById('service-time');
const notes = document.getElementById('notes-widget');

if(procedure){
    ReactDOM.render(<ProcedureViews />, procedure);
}
if(inventory){
    ReactDOM.render(<InventorySelectWidgets />, inventory)
}
if(personnel){
    const splitURL = window.location.href.split('/');
    const tail = splitURL[splitURL.length - 1];
    let populatedURL  = null;
    if(tail !== 'team-create'){
        populatedURL = '/services/api/team/'+ tail;
    }

    const resProcessor = (res) =>{
        return res.data.members.map((m) =>{
            return(m.id + '-' + m.name)
        });
    }
    ReactDOM.render(<MultipleSelectWidget 
                        title="Select Service People"
                        dataURL="/services/api/service-person/"
                        inputField="members"
                        populatedURL={populatedURL}
                        resProcessor={resProcessor}/>, personnel)
}
if(workOrderPersons){
    const splitURL = window.location.href.split('/');
    const tail = splitURL[splitURL.length - 1];
    let populatedURL  = null;
    if(tail !== 'team-create'){ // TODO fix
        populatedURL = '/services/api/work-order/'+ tail;
    }

    const resProcessor = (res) =>{
        return res.data.service_people.map((sp) =>{
            return(sp.id + '-' + sp.name)
        });
    }
    ReactDOM.render(<MultipleSelectWidget 
                        title="Select Service People"
                        dataURL="/services/api/service-person/"
                        inputField="service_people"
                        populatedURL={populatedURL}
                        resProcessor={resProcessor}/>, workOrderPersons)
}
if (consumableTable){
    ReactDOM.render(<GenericTable
        fieldDescriptions={['Item', 'Unit', 'Quantity']}
        fieldOrder={['item', 'unit', 'quantity']}
        formInputID='id_consumables'
        fields={[
            {
                name: 'item',
                type: 'search',
                width: 25,
                url: '/inventory/api/consumable/',                idField: 'id',
                displayField: 'name',
                required: true,
            },
            {
                name: 'unit',
                type: 'select',
                width: 15,
                required: true,
                url: '/inventory/api/unit/'
            },
            {
                name: 'quantity',
                type: 'number',
                width: 15,
                required: true
            }
        ]} />, consumableTable)
}
if (equipmentTable){
    ReactDOM.render(<GenericTable
        fieldDescriptions={['Item', 'Condition', 'Quantity']}
        fieldOrder={['item', 'condition', 'quantity']}
        formInputID='id_equipment'
        fields={[
            {
                name: 'item',
                type: 'search',
                width: 30,
                url: "/inventory/api/equipment/", 
                idField: 'id',
                displayField: 'name',
                required: true,
            },
            {
                name: "condition",
                type: "widget",
                widgetCreator: (comp) =>{
                    return(
                        <select
                            className="form-control"
                            onChange={(evt) =>{
                                let newData = {...comp.state.data};
                                newData['condition'] = evt.target.value;
                                comp.setState({data: newData});
                            }}>
                            <option value="">-------</option>
                            {['excellent', 'good', 'poor', 'broken'].map(
                                (el, i) =>{
                                    return(<option 
                                                key={i}
                                                value={el}>{el}</option>)
                            })}
                        </select>
                    )
                }
            },
            {
                name: 'quantity',
                type: 'number',
                width: 15,
                required: true
            }
        ]} />, equipmentTable)
}

if(serviceTime){
    ReactDOM.render(<GenericTable
        formInputID="id_service_time"
        fieldOrder={['date','employee', 'normal_time', 'overtime']}
        fields={[
            {
                'name': 'date',
                'type': 'widget',
                'width': 25,
                'required': true,
                'widgetCreator': (comp) =>{
                    return <input type="date" 
                                    className="form-control"
                                    onChange={(evt) =>{
                                        let newData = {...comp.state.data};
                                        newData['date'] = evt.target.value;
                                        comp.setState({data: newData}); 
                                    }} />
                }
            },
            {
            'name': 'employee',
            'type': 'search',
            'width': 25,
            'url' :'/employees/api/employee',
            'idField': 'employee_number',
            'displayField': 'first_name',
            'required': true
        },
        {
            'name': 'normal_time',
            'type': 'widget',
            'width': 25,
            'required': true,
            'widgetCreator': (comp) =>{
                return <TimeField 
                    initial=""
                    name="normal_time"
                    handler={(data, name) =>{
                        if(data.valid){
                            let newData = {...comp.state.data};
                            newData['normal_time'] = data.value;
                            comp.setState({data: newData});    
                        }
                    }}/>
            }
        },
        {
            'name': 'overtime',
            'type': 'widget',
            'width': 25,
            'required': true,
            'widgetCreator': (comp) =>{
                return <TimeField 
                    initial=""
                    name="overtime"
                    handler={(data, name) =>{
                        if(data.valid){
                            let newData = {...comp.state.data};
                            newData['overtime'] = data.value;
                            comp.setState({data: newData});    
                        }
                    }}/>
            }
        }
    ]}
        fieldDescriptions={['Date','Employee', 'Normal Time(Hours)', 'Overtime(Hours)']}
        />, serviceTime)
}

if(notes){
    const splitURL = window.location.href.split('/');
    const tail = splitURL[splitURL.length - 1];
    const target='work_order';
    const token= document.querySelector(
        'input[name="csrfmiddlewaretoken"]').value;
    ReactDOM.render(<NotesWidget 
        dataURL={'/base/api/notes/service/' + tail}
        token={token}
        target={target}
        targetID={tail} />, notes)
}
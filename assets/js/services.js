import React from 'react';
import ReactDOM from 'react-dom';
import {ProcedureViews, InventorySelectWidgets} from '../js/services/procedure';
import MultipleSelectWidget from '../js/src/components/multiple_select';
import GenericTable from './src/generic_list/containers/root';

const procedure = document.getElementById('procedure-widgets');
const inventory = document.getElementById('inventory-widgets');
const personnel = document.getElementById('personnel-list');
const consumableTable = document.getElementById('consumable-requisition-table');
const equipmentTable = document.getElementById('equipment-requisition-table');
const workOrderPersons = document.getElementById('work-order-persons');

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
            return({
                value: m.id + '-' + m.name,
                clicked: false
            })
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
    if(tail !== 'team-create'){
        populatedURL = '/services/api/work-order/'+ tail;
    }

    const resProcessor = (res) =>{
        return res.data.service_people.map((sp) =>{
            return({
                value: sp.id + '-' + sp.name,
                clicked: false
            })
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
        formInputID='id_items'
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
        formInputID='id_items'
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
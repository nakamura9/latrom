import React from 'react';
import ReactDOM from 'react-dom';
import {ProcedureViews, InventorySelectWidgets} from '../js/services/procedure';
import MultipleSelectWidget from '../js/src/multiple_select';
import ConsumableRequisitionTable from './services/requisition/consumable';
import EquipmentRequisitionTable from './services/requisition/equipment';


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
        //const pk =  splitURL[splitURL.length - 2];
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
    ReactDOM.render(<ConsumableRequisitionTable />, consumableTable)
}
if (equipmentTable){
    ReactDOM.render(<EquipmentRequisitionTable />, equipmentTable)
}
import React, {Component} from 'react';
import MultipleSelectWidget from '../src/components/multiple_select';
import TextBoxListWidget from '../src/text_box_list';
import $ from 'jquery';
import axios from 'axios';

class ProcedureViews extends Component{
    render(){
        const splitURL = window.location.href.split('/');
        const tail = splitURL[splitURL.length - 1];
        let populatedURL  = null;
        if(tail !== 'create-procedure'){
            const pk =  splitURL[splitURL.length - 2];
            populatedURL = '/services/api/procedure/'+ pk;
        }

        return(
            <div>
                <TextBoxListWidget 
                    title="Procedure Steps"
                    fieldName="tasks"
                    populatedURL={populatedURL}
                    resProcessor={(res) => (res.data.steps.map((step) => (step.description)))}/>    
            </div>
        )
    }
}

const InventorySelectWidgets = (props) => {
    const splitURL = window.location.href.split('/');
    const tail = splitURL[splitURL.length - 1];
    let populatedURL  = null;
    if(tail !== 'create-procedure'){
        const pk =  splitURL[splitURL.length - 2];
        populatedURL = '/services/api/procedure/'+ pk;
    }
    
    return(
        <div>
            <MultipleSelectWidget 
                title="Select Equipment"
                dataURL = '/inventory/api/equipment/'
                inputField = 'equipment'
                populatedURL = {populatedURL}
                resProcessor = {(res) =>{
                     return res.data.required_equipment.map((c) => (
                        {
                            value: c.id + '-' + c.name,
                            clicked: false
                        }
                    ))}}
                />
            <MultipleSelectWidget 
                title="Select Consumables"
                dataURL = '/inventory/api/consumable/'
                inputField = 'consumables'
                populatedURL = {populatedURL}
                resProcessor = {(res) =>{
                    return res.data.required_consumables.map((c) => (
                        {
                            value: c.id + '-' + c.name,
                            clicked: false
                        }
                    ))}}
                />
        </div>
    )
}

export {ProcedureViews, InventorySelectWidgets}; 
import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import ShiftSchedule from './manufacturing/shifts/container/root';
import MultipleSelectWidget from '../js/src/components/multiple_select';
import GenericTable from '../js/src/generic_list/containers/root';
import ProcessRoot from '../js/manufacturing/process/containers/root';

const scheduleTable = document.getElementById('schedule-table');
const machineGroup = document.getElementById('machine-group');
const productList = document.getElementById('product-list');
const billOfMaterialsTable = document.getElementById('raw-materials-table');
const process = document.getElementById('process');

if(scheduleTable){
    ReactDOM.render(<ShiftSchedule />, scheduleTable);
}else if(machineGroup){
    let resProcessor = (res) =>{
        return res.data.map((m) =>{
            return({
                value: m.id + '-' + m.name,
                clicked: false
            })
        });
    };
    ReactDOM.render(<MultipleSelectWidget 
                        title="Select Machines"
                        inputField="machines"
                        resProcessor={resProcessor}
                        dataURL="/manufacturing/api/process-machine/"
                        />, machineGroup)
}else if(productList){
    let resProcessor = (res) =>{
        return res.data.map((p) =>{
            return({
                value: p.id + '-' + p.name,
                clicked: false
            })
        });
    };

    ReactDOM.render(
        <MultipleSelectWidget 
            title="Select Products"
            inputField="products"
            resProcessor={resProcessor}
            dataURL="/manufacturing/api/process-product/"/>, productList
    );
}else if(billOfMaterialsTable){
    ReactDOM.render(<GenericTable 
                        hasLineTotal={false}
                        hasTotal={false}
                        fieldOrder={['product', 'quantity', 'unit']}
                        formInputID="id_products"
                        fields={[
                            {
                                name: 'product',
                                type: 'search',
                                width: 40,
                                required: true,
                                url: '/manufacturing/api/process-product/',
                                idField: 'id',
                                displayField: 'name'
                            },
                            {
                                name: 'quantity',
                                type: 'number',
                                width: 15,
                                required: true
                            },
                            {
                                name: 'unit',
                                type: 'select',
                                url: '/inventory/api/unit/',
                                asyncResPRocessor: function(res){
                                    return(res.data.map((item)=>({
                                        value: item.id,
                                        name: item.name
                                    })   
                                    ))
                                },
                                width: 15,
                                required: true
                            }
                        ]}
                        />, billOfMaterialsTable)
}else if(process){
    ReactDOM.render(
        <ProcessRoot />, process
    )
}
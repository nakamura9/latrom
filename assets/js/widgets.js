import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TreeSelectWidget from '../js/src/tree_select_widget';
import axios from 'axios';
import MessageDetail from '../js/messaging/container/root';
import MultipleSelectWidget from "./src/multiple_select/containers/root";
import PaginatedList from '../js/src/paginated_list/containers/root';
import PricingWidget from "../js/inventory/pricing_widget";
import MutableTable from "../js/src/mutable_table/container/root";
import GenericTable from '../js/src/generic_list/containers/root';
import TimeField from '../js/src/components/time_field';

const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');
const threadView = document.getElementById('thread-widget');
const testView = document.getElementById('test');
const pricing = document.getElementById('pricing-widget');

const dataMapper = (node, i) =>{
    
    return({
        label: node.name,
        nodes: node.children,
        id: node.id
    });
}

const currentWarehouse = () =>{
    let decomposed = window.location.href.split('/');
    return(decomposed[decomposed.length-1])
}
if(storageMedia){
    const pk = currentWarehouse();
    axios.get('/inventory/api/storage-media-detail/' + pk).then(
        res => {
            ReactDOM.render(<TreeSelectWidget 
                url={'/inventory/api/storage-media-nested/' + res.data.warehouse}
                externalFormFieldName='location'
                updateUrlRoot='/inventory/storage-media-update/'
                detailUrlRoot='/inventory/storage-media-detail/'
                dataMapper={dataMapper}/>, storageMedia);
        }
    )
    
}else if(category){
    ReactDOM.render(<TreeSelectWidget 
        url='/inventory/api/category'
        externalFormFieldName='parent'
        dataMapper={dataMapper}/>, category);
}else if(categoryView){
    ReactDOM.render(<TreeSelectWidget 
        isListView={true}
        updateUrlRoot='/inventory/category-update/'
        detailUrlRoot='/inventory/category-detail/'
        url='/inventory/api/category'
        externalFormFieldName='parent'
        dataMapper={dataMapper}/>, categoryView);
}else if(storageMediaView){
    let pk = currentWarehouse();
    ReactDOM.render(<TreeSelectWidget
        isListView={true} 
        url={'/inventory/api/storage-media-nested/' + pk}
        externalFormFieldName='location'
        updateUrlRoot='/inventory/storage-media-update/'
        detailUrlRoot='/inventory/storage-media-detail/'
        dataMapper={dataMapper}/>, storageMediaView);
}else if(threadView){
    ReactDOM.render(<MessageDetail />, threadView);
}else if(testView){
    ReactDOM.render(<GenericTable
        formInputID="form"
        fieldOrder={['employee', 'normal_time', 'overtime']}
        fields={[{
            'name': 'employee',
            'type': 'search',
            'width': 50,
            'url' :'/employees/api/employee',
            'idField': 'employee_number',
            'displayField': 'first_name'
        },
        {
            'name': 'normal_time',
            'type': 'widget',
            'width': 25,
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
        fieldDescriptions={['Employee', 'Normal Time(Hours)', 'Overtime(Hours)']}
        />, testView);
}else if(pricing){
    ReactDOM.render(<PricingWidget />, pricing);
}

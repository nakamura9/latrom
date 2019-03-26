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
import NoteWidget from '../js/src/notes_widget/root';
import SearchableWidget from '../js/src/components/searchable_widget';
import InvoiceTable from '../js/invoices/invoice';

const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');
const threadView = document.getElementById('thread-widget');
const testView = document.getElementById('test');
const pricing = document.getElementById('pricing-widget');
const depts = document.getElementById('department-list');
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
    ReactDOM.render(<InvoiceTable itemList={[]} />, testView);
}else if(pricing){
    ReactDOM.render(<PricingWidget />, pricing);
}else if(depts){
    ReactDOM.render(<TreeSelectWidget 
        isListView={true}
        updateUrlRoot='/employees/department/update/'
        detailUrlRoot='/employees/department/detail/'
        url='/employees/api/department'
        externalFormFieldName='parent_department'//not important
        dataMapper={dataMapper}/>, depts);
}

import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TreeSelectWidget from '../js/src/tree_select_widget';
import axios from 'axios';
import PricingWidget from "../js/inventory/pricing_widget";
import {ImgPreview} from '../js/src/common';
import FilePickerUI from '../js/src/components/custom_file_picker';
import TimelineWidget from '../js/src/timeline/container/root';
import StepsWidget from '../js/src/steps/container/root';

const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');
const testView = document.getElementById('test');
const pricing = document.getElementById('pricing-widget');
const depts = document.getElementById('department-list');
const avatar = document.getElementById('avatar-preview');

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
}else if(testView){
    ReactDOM.render(<StepsWidget />, testView);
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
}else if(avatar){
    ReactDOM.render(<ImgPreview 
                        inputID='id_avatar'
                        url='/messaging/user-icon/' />, avatar);
}

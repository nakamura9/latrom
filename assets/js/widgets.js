import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TreeSelectWidget from '../js/src/tree_select_widget';

const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');


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
    let pk = currentWarehouse();
    ReactDOM.render(<TreeSelectWidget 
        url={'/inventory/api/storage-media/' + pk}
        fieldName='location'
        selectFunc={(id) => (null)}
        dataMapper={dataMapper}/>, storageMedia);
}else if(category){
    ReactDOM.render(<TreeSelectWidget 
        url='/inventory/api/category'
        fieldName='parent'
        selectFunc={(id) => (null)}
        dataMapper={dataMapper}/>, category);
}else if(categoryView){
    ReactDOM.render(<TreeSelectWidget 
        url='/inventory/api/category'
        fieldName='parent'
        selectFunc={(id) =>{
            document.getElementById('id_category_detail').href = 
            '/inventory/category-detail/' + id;
            document.getElementById('id_category_update').href = 
            '/inventory/category-update/' + id;
        }}
        dataMapper={dataMapper}/>, categoryView);
}else if(storageMediaView){
    console.log('selected storage media');
    let pk = currentWarehouse();
    ReactDOM.render(<TreeSelectWidget 
        url={'/inventory/api/storage-media/' + pk}
        fieldName='location'
        selectFunc={(id) =>{
            document.getElementById('id_storage_media_detail').href = 
            '/inventory/storage-media-detail/' + id;
            document.getElementById('id_storage_media_update').href = 
            '/inventory/storage-media-update/' + id;
        }}
        dataMapper={dataMapper}/>, storageMediaView);
}

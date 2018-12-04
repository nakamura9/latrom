import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TreeSelectWidget from '../js/src/tree_select_widget';
import axios from 'axios';
import MessageDetail from '../js/messaging/container/root';
import GenericTable from './src/generic_list/containers/root';

const storageMedia = document.getElementById('storage-media-select-widget');
const category = document.getElementById('category-select-widget');
const categoryView = document.getElementById('category-tree-view');
const storageMediaView = document.getElementById('storage-media-tree-view');
const threadView = document.getElementById('thread-widget');
const testView = document.getElementById('test');

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
    const calculateTotalFunc = (data)=>{
        return(data.quantity * data.price);
    }

    const priceGetter = (comp, fieldName, pk) =>{
        axios({
            url: '/inventory/api/product/' + pk,
            method:'get'
        }).then(res => {
            let newData = {...comp.state.data};
            newData[fieldName] = parseFloat(res.data.unit_sales_price)
                                        .toFixed(2);
            comp.setState({data: newData});
        });
    }

    ReactDOM.render(<GenericTable 
                        hasLineTotal={true}
                        calculateTotal={calculateTotalFunc}
                        fieldOrder={['product', 'quantity', 'price']}
                        formInputID={'form-input'}
                        fields={[
                            {
                                name: 'product',
                                required: true,
                                type: 'search',
                                width: 40,
                                url: '/inventory/api/product/',
                                idField: 'id',
                                canCreateNewItem: true,
                                newLink: '/inventory/product-create/',
                                displayField: 'name',
                            },
                            
                            {
                                required: false,
                                name: 'quantity',
                                type: 'number',
                                width: 15
                            },
                            {
                                required: false,
                                name: 'price',
                                type: 'fetch',
                                width: 15,
                                dataGetter: priceGetter
                            },
                        ]}/>, testView);
}

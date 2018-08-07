import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import axios from 'axios';
import {Totals, DeleteButton, SearchableWidget} from '../src/common';

export default class SalesInvoiceForm extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
        }
    }
    addItem = (data) => {
        data['subtotal'] = data.quantity * data.unit_price;
        let newItems = [...this.state.items];
        newItems.push(data);
        this.setState({items:newItems}, () => {this.updateForm()});
        
    }

    removeItem = (index) => {
        let newItems = [...this.state.items];
        newItems.splice(index, 1);
        this.setState({items: newItems}, () => {this.updateForm()});
    }
    
    componentDidMount(){
        $('<input>').attr({
            'type': 'hidden',
            'value': '',
            'name': 'item_list',
            'id': 'id_item_list'
        }).appendTo('form');
        // get config
        $.ajax({
            'url': '/invoicing/api/config/1',
            'method': 'GET'
        }).then(
            res => {
                this.setState({taxRate: res.sales_tax});
            }
        );
        //check if the page is an update
        let URL = window.location.href;
        let decomposed = URL.split('/');
        let tail = decomposed[decomposed.length - 1];
        
        if(tail !== 'create-sales-invoice'){
            axios({
                url: '/invoicing/api/sales-invoice/' + tail,
                method: 'GET',
            }).then(res =>{
                console.log(res);
                let itemList = res.data.salesinvoiceline_set.map((line) =>{
                    return {
                        item_name: line.item.code + '-' + line.item.item_name,
                        unit_price: line.item.unit_sales_price,
                        quantity: line.quantity,
                        subtotal: parseFloat(line.quantity) * 
                            parseFloat(line.item.unit_sales_price)
                    }
                })
                this.setState({items: itemList}, this.updateForm);
            });
        }
    }

    updateForm(){
        $('#id_item_list').val(
            encodeURIComponent(
                JSON.stringify(this.state.items)
            )
        );
    }


    render(){
        let theadStyle = {
            padding: '2mm',
            borderRight: '1px solid white',
            color: 'white',
            backgroundColor: 'black'
        };
        return(
            <table className="table">
                <thead>
                    <tr style={theadStyle}>
                        <th style={{width:"10%"}}></th>
                        <th style={{width:"50%"}}>Item</th>
                        <th style={{width:"100%"}}>Unit Price</th>
                        <th style={{width:"15%"}}>Quantity</th>
                        <th style={{width:"15%"}}>Line total</th>
                    </tr>
                </thead>
                <tbody>
                    { this.state.items.map((item, i) => (
                        <SalesLine 
                            key={i}
                            index={i}
                            item={item}
                            handler={this.removeItem}/>
                    ))}
                    <EntryRow addItem={this.addItem.bind(this)}/>
                </tbody>
                <Totals
                    span={5}
                    list={this.state.items}
                    subtotalReducer={function(x, y){
                        return (x + y.subtotal);
                    }}/>
            </table>
        );
    }
}
const SalesLine = (props) => {
    return(
        <tr >
            <td>
                <DeleteButton 
                    handler={props.handler}
                    index={props.index}/>
            </td>
            <td>{props.item.item_name.split('-')[1]}</td>
            <td>{props.item.unit_price.toFixed(2)}</td>
            <td>{props.item.quantity}</td>
            <td>{props.item.subtotal.toFixed(2)}</td>
        </tr>
    )
}

class EntryRow extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
            inputs: {
                unit_price:0.0
            }
        };   
    }
    componentDidMount(){
        $.ajax({
            url: '/inventory/api/item/',
            method: 'GET'
        }).then(res =>{
            this.setState({items: res});
        });
    }
    clickHandler(){
        this.props.addItem(this.state.inputs);
    }

    inputHandler(evt){
        let name = evt.target.name;
        let newInputs = {...this.state.inputs};
        newInputs[name] = evt.target.value;
        this.setState({inputs:newInputs});
    }

    onSelect =(value) =>{
        const decomposed = value.split('-');
        const pk = decomposed[0];
        const item_name = decomposed[1];
        axios({
            url: '/inventory/api/item/' + pk,
            method:'get'
        }).then(res => {
            console.log(res.data);
            let newInputs = {...this.state.inputs};
            newInputs['unit_price'] = res.data.unit_sales_price;
            newInputs['item_name'] = value;
            this.setState({inputs: newInputs});
        });
        }

    onClear = () => {
        this.setState({inputs: {
            'unit_price':0.00
        }})
    }
    
    render(){
        return(
            <tr>
                <td colSpan={2}>
                    <SearchableWidget 
                        dataURL="/inventory/api/item/"
                        displayField="item_name"
                        idField="code"
                        onSelect={this.onSelect}
                        onClear={this.onClear}
                    />
                </td>
                
                <td>{this.state.inputs.unit_price.toFixed(2)}</td>
                <td>
                    <input 
                        type="number" 
                        name="quantity"
                        onChange={this.inputHandler.bind(this)}
                        className="form-control"
                        value={this.state.inputs.quantity}
                        placeholder="Quantity..." />
                </td>
                <td>
                    <button 
                        className="btn btn-primary"
                        onClick={this.clickHandler.bind(this)}
                        type="button">
                        Insert
                    </button>
                </td>
            </tr>
                );
    }
}
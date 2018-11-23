import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import axios from 'axios';
import {Totals, DeleteButton, SearchableWidget} from '../src/common';

export default class SalesInvoiceForm extends Component{
    state = {
            items: [],
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
                console.log(res.data);
                let itemList = res.data.salesinvoiceline_set.map((line) =>{
                    return {
                        item_name: line.product.id + '-' + line.product.name,
                        unit_price: line.product.unit_sales_price,
                        quantity: line.quantity,
                        subtotal: parseFloat(line.quantity) * 
                            parseFloat(line.product.unit_sales_price)
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
        const theadStyle = {
            padding: '2mm',
            borderRight: '1px solid white',
            color: 'white',
            backgroundColor: '#07f'
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
                    <EntryRow 
                        itemList={this.state.items}
                        addItem={this.addItem.bind(this)}/>
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
//item -ok
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
    state = {
            items: [],
            inputs: {
                unit_price:0.0,
                quantity: 0.0
            }
        }
    componentDidMount(){
        $.ajax({
            url: '/inventory/api/product/',
            method: 'GET'
        }).then(res =>{
            this.setState({items: res});
        });
    }
    clickHandler =() => {
        if(this.state.inputs.quantity <= 0.0){
            alert('Please enter a valid quantity');
            return;
        }
        this.props.addItem(this.state.inputs);
    }

    inputHandler = (evt) =>{
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
            url: '/inventory/api/product/' + pk,
            method:'get'
        }).then(res => {
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
    
    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                inputs: {
                    unit_price:0.0,
                    quantity: 0.0
                }
            })
            //remove selected choice from list of choices 
        }
    }


    render(){
        const theadStyle = {
            padding: '2mm',
            borderRight: '1px solid white',
            color: 'white',
            backgroundColor: '#07f'
        };
        return(
            <tr style={theadStyle}>
                <td colSpan={2}>
                    <SearchableWidget 
                        list={this.props.itemList}
                        dataURL="/inventory/api/product/"
                        displayField="name"
                        idField="id"
                        onSelect={this.onSelect}
                        onClear={this.onClear}
                    />
                        <button 
                            style={{width:"100%"}}
                            className="btn "
                            onClick={() => window.open(
                                '/inventory/product-create/' ,'popup','width=900,height=480')}>
                            Create New Product <i className="fas fa-plus"></i>
                        </button>
                   
                </td>
                <td>{this.state.inputs.unit_price.toFixed(2)}</td>
                <td>
                    <input 
                        type="number" 
                        name="quantity"
                        onChange={this.inputHandler}
                        className="form-control"
                        value={this.state.inputs.quantity}
                        placeholder="Quantity..." />
                </td>
                <td>
                    <button 
                        className="btn "
                        onClick={this.clickHandler}
                        type="button">
                        Insert
                    </button>
                </td>
            </tr>
                );
    }
}
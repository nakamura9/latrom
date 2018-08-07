import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {SearchableWidget, Totals, Aux, DeleteButton} from '../src/common';
import $ from 'jquery';
import axios from 'axios';

export default class OrderTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            contents: [],
            total: 0
        }
    }

    componentDidMount(){
        //set up the hidden input 
        $('<input>').attr({
            type: 'hidden',
            name: 'items',
            id: "id_items" ,
            value: ""
        }).appendTo('form');
        //check if an update occured
        var url = window.location.href;
        var url_elements = url.split("/");
        var tail = url_elements[url_elements.length - 1];
        if(tail !== 'order-create'){
            axios({
                url: '/inventory/api/order/' + tail + "/",
                method: 'GET'
            }).then(res => {
                let newContents = res.data.orderitem_set.map((item, i) =>{
                    return({
                        pk: item.item.code,
                        name: item.item.item_name,
                        quantity: item.quantity,
                        order_price: item.order_price,
                        subtotal: item.order_price * item.quantity
                    })
                })
                this.setState({contents: newContents}, this.updateForm)
            });
        }
    }
    
    insertHandler = (vals) => {
        var newContents = [...this.state.contents];
        newContents.push({
            ...vals,
        subtotal: vals.quantity * vals.order_price});
        this.setState({contents: newContents}, this.updateForm);

        }

    updateForm =() =>{
        $('#id_items').val(
            encodeURIComponent(
                JSON.stringify(this.state.contents)
            )
        );
    }
    
    removeHandler = (id) => {
        var newContents = [...this.state.contents];
        newContents.splice(id, 1);
        this.setState({contents: newContents}, this.updateForm);
    }

    render(){
        let headStyle = {
            color: "white",
            backgroundColor: 'black',
            borderRight: '1px solid white',
            padding: '15px'
        }
        return(
            <table>
                <thead>
                    <tr >
                        <td style={{
                            ...headStyle,
                            width:'10%'
                            }}></td>
                        <th style={{
                            ...headStyle,
                            width:'50%'
                            }}>Item</th>
                        <th style={{
                            ...headStyle,
                            width:'10%'
                            }}>Quantity</th>
                        <th style={{
                            ...headStyle,
                            width:'15%'
                            }}>Order Price</th>
                        <th style={{
                            ...headStyle,
                            width:'15%'
                            }}>Line Total</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.contents.map((item, i) =>{
                        return(
                            <tr key={i}>
                                <td>
                                    <DeleteButton 
                                        handler={this.removeHandler}
                                        index={i}/>
                                </td>
                                <td>{item.name}</td>
                                <td>{item.quantity}</td>
                                <td>{item.order_price}</td>
                                <td>{item.subtotal}</td>
                            </tr>
                        )
                    })}
                <OrderTableEntry 
                    insertHandler={this.insertHandler} />
                </tbody>
                
                <Totals 
                    span={5}
                    list={this.state.contents}
                    subtotalReducer={function(x, y){
                        return(x + y.subtotal);
                    }}/>
            </table>
        )
    }
}

class OrderTableEntry extends Component{
    state = {
        inputs: {
            quantity: 0,
            order_price: 0
        }
    }
    
    insertHandler =() =>{
        this.props.insertHandler(this.state.inputs);
    }

    inputHandler =(event) =>{
        var name= event.target.name;
        var value = event.target.value;
        var newVals = {...this.state.inputs};
        newVals[name] = value;
        this.setState({inputs: newVals});
    }

    onSearchableSelect =(val) =>{
        let newInputs = {...this.state.inputs};
        let pk;
        let name;
        [pk, name] = val.split('-');
        newInputs['name'] = name;
        newInputs['pk'] = pk;
        this.setState({inputs:newInputs});
    }

    onSearchableClear =() =>{
        let newInputs = {...this.state.inputs};
        newInputs['name'] = "";
        this.setState({inputs:newInputs});
    }

    render(){
        return(
            <Aux>
                <tr>
                    <td colSpan={2}>
                        <SearchableWidget 
                            dataURL="/inventory/api/item"
                            idField="code"
                            displayField="item_name"
                            onSelect={this.onSearchableSelect}
                            onClear={this.onSearchableClear}/>
                    </td>
                    <td>
                        <input 
                            name="quantity"
                            type="text"
                            className="form-control"
                            value={this.state.inputs.quantity}
                            onChange={this.inputHandler}/>
                    </td>
                    <td>
                        <input 
                            name="order_price"
                            type="text"
                            className="form-control"
                            value={this.state.inputs.order_price}
                            onChange={this.inputHandler}/>
                    </td>
                    <td>
                    <button type="button" 
                    className="btn btn-primary btn-lg"
                    onClick={this.insertHandler}>Insert</button>
                    </td>
                </tr>
            </Aux>
        );
    }
}
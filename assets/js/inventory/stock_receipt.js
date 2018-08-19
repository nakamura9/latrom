import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import {SearchableWidget} from '../src/common'

const PK = $('#id_warehouse').val()

export default class ItemReceiptTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            'items': [],
            receivedItems: []
        }
    }
    componentDidMount(){
        let order = document.getElementById('id_order').value;
        $.ajax({
            url: '/inventory/api/order/' + order,
            'method': 'GET'
        }).then(
            res => {
                this.setState({
                    'items': res.orderitem_set.filter((item, i) =>{
                        return(item.quantity > item.received);
                    })
                });
            }
        );
        $('<input>').attr({
            'name': 'received-items',
            'type': 'hidden',
            'value': '',
            'id': 'id-received-items'
        }).appendTo('form');

    }

    receiveHandler = (data) =>{
        let newReceived = [...this.state.receivedItems];
        newReceived.push(data);
        this.setState({receivedItems: newReceived}, this.updateForm);
        
    }

    updateForm = () =>{ 
        $('#id-received-items').val(encodeURIComponent(
            JSON.stringify(this.state.receivedItems)
        ));
    }
    
    render(){
        let lines = null;
        if(this.state.items.length === 0){
            lines = (<tr>
                        <td colSpan="4">
                            <center>
                                No more items to be received for this order
                            </center>
                        </td>
                    </tr>);
        }else{
            lines = this.state.items.map((item, i) => (
                <ReceivingLine 
                    key={i}
                    item={item}
                    receiveHandler={this.receiveHandler} />
            ));  
        }
        return(
            <table className="table">
                <thead>
                    <tr className="bg-primary text-white">
                        <th style={{width:"15%"}}>Item Name</th>
                        <th style={{width:"10%"}}>Ordered Quantity</th>
                        <th style={{width:"10%"}}>Quantity Already Received</th>
                        <th style={{width:"10%"}}>Quantity</th>
                        <th style={{width:"45%"}}>Receiving Location</th>
                        <th style={{width:"10%"}}></th>
                    </tr>
                </thead>
                <tbody>
                    {lines}             
                </tbody>
            </table>
        );
    }
}

class ReceivingLine extends Component{
    state = {
        orderItem: this.props.item.id,
        quantity: 0,
        medium: ""
    }
    updateQuantity = (evt) =>{
        this.setState({quantity: evt.target.value});
    }
    onSelectMedium = (data) =>{
        console.log(data);
        this.setState({medium: data});
    }
    onClearMedium = () =>{
        this.setState({medium:""})
    }
    render(){
        return(
            <tr>
                <td>{this.props.item.product.name}</td>
                <td>{this.props.item.quantity}</td>
                <td>{this.props.item.received}</td>
                <td><input type="number" 
                    name={"item-" + this.props.item.id}
                    value={this.state.quantity}
                    className="form-control"
                    onChange={this.updateQuantity} /></td>
                <td>
                    <SearchableWidget
                        dataURL={"/inventory/api/storage-media/" + PK}
                        displayField="name"
                        idField="id"
                        onSelect={this.onSelectMedium}
                        onClear={this.onClearMedium}/>
                </td>
                <td>
                    <button 
                        className="btn btn-primary"
                        onClick={() => this.props.receiveHandler(this.state)}>Receive</button>
                </td>
            </tr>
        )
    }
    
}
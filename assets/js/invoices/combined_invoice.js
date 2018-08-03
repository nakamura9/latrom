import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget} from '../src/common';
import EntryWidget from './combinedInvoice/entry_widget';


export default class CombinedTable extends Component{
    state = {
        taxObj: null,
        tax: 0.0,
        subtotal: 0.0,
        total: 0.0,
        items: []
    }

    componentDidMount(){
        $('<input>').attr({
            type: 'hidden',
            value: '',
            id: 'id_item_list',
            name: 'item_list'
        }).appendTo('form');
    }
    
    insertHandler = (data) =>{
        let newItems = [...this.state.items];
        newItems.push(data);
        this.setState({items: newItems}, this.updateForm);
    }

    deleteHandler = (index) =>{
        let newItems = [...this.state.items];
        newItems.splice(index, 1);
        this.setState({items: newItems}, this.updateForm);
        
    }

    updateForm = () => {
        $('#id_item_list').val(
            encodeURIComponent(JSON.stringify(this.state.items))
        );
    }

    render(){
        return(
            <table className="table">
                <thead>
                    <tr style={{
                        padding: '2mm',
                        color: 'white',
                        backgroundColor: 'black',
                        width: '100%'
                    }}>
                        <th style={{width:"10%"}}></th>
                        <th style={{width:"70%"}}>Description</th>
                        <th style={{width:"20%"}}>Line Total</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.items.map((item, i) =>{
                        let line;
                        if(item.lineType === "sale"){
                            line = <SaleLine 
                                        {...item.data}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }else if(item.lineType === "service"){
                            line = <ServiceLine  
                                        {...item.data}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }else{
                            line = <BillableLine  
                                        {...item.data}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }
                        return(line);
                    }
                    )}
                <EntryWidget 
                    insertHandler={this.insertHandler}/>
                </tbody>
                <tfoot>
                    <tr>
                        <th colSpan={2}>Subtotal</th>
                        <td>{this.state.subtotal}</td>
                    </tr>
                    <tr>
                        <th colSpan={2}>Tax</th>
                        <td>{this.state.tax}</td>
                    </tr>
                    <tr>
                        <th colSpan={2}>Total</th>
                        <td>{this.state.total}</td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}

const SaleLine = (props) =>{
    let total = props.price * parseFloat(props.quantity);
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>
                {props.quantity} x {
                    props.item.split('-')[1]
                } @ ${props.price.toFixed(2)} each.
            </td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

const ServiceLine = (props) =>{
    let total = (props.hours * props.rate) + props.flatFee;
    return(
        <tr>
            <td>
                <DeleteButton
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{
                props.service.split('-')[1]
            } - Flat Fee: ${props.flatFee} + {props.hours}Hrs x @ ${props.rate} /Hr</td>
            <td>{total}</td>
        </tr>
    )
}

const BillableLine = (props) =>{
    console.log(props);
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{props.description}</td>
            <td>{props.amount}</td>
        </tr>
    )
}

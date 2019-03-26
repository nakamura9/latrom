import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, Totals} from '../src/common';
import EntryWidget from './invoice_entry';


export default class InvoiceTable extends Component{
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

         //check if the page is an update
         let URL = window.location.href;
         let decomposed = URL.split('/');
         let tail = decomposed[decomposed.length - 1];
         
         if(tail !== 'create-invoice'){
             axios({
                 url: '/invoicing/api/invoice/' + tail,
                 method: 'GET',
             }).then(res =>{
                 let itemList = res.data.invoiceline_set.map((line) =>{
                    let lineMappings = {
                        1: 'product',
                        2: 'service',
                        3: 'expense'
                    };
                    let data;
                    if(line.line_type === 1){
                        data = {
                            selected: line.product.product.id + '-' + line.product.product.name,
                            quantity: parseFloat(line.product.quantity),
                            unitPrice: parseFloat(line.product.price)
                        };
                    }else if (line.line_type === 2){
                        data = {
                            service: line.service.id + '-' + line.service.name,
                            hours: line.quantity_or_hours,
                            rate: line.service.hourly_rate,
                            flatFee: line.service.flat_fee
                        }
                    }else if (line.line_type === 3){
                        data = {
                            expense: line.expense.id + '-' +line.expense.description,
                            description: line.expense.description,
                            amount: line.expense.amount 
                        }
                    }
                    return {
                        type: lineMappings[line.line_type],
                        ...data
                     }
                 })
                 this.setState({items: itemList}, this.updateForm);
             });
        }
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

    subtotalReducer(x, y){
        if(y.type === 'product'){
            let total = y.unitPrice * parseFloat(y.quantity);
            return (x + total);
        }else if(y.type === 'service'){
            let total = parseFloat((y.rate) * parseFloat(y.hours)) + 
                parseFloat(y.fee);
            return (x + total);
        }else{
            //billable
            return (x + parseFloat(y.amount));
        }
    }

    render(){
        return(
            <table className="table">
                <thead>
                    <tr style={{
                        padding: '2mm',
                        color: 'white',
                        backgroundColor: '#07f',
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
                        if(item.type === "product"){
                            line = <SaleLine 
                                        {...item}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }else if(item.type === "service"){
                            line = <ServiceLine  
                                        {...item}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }else{
                            line = <BillableLine  
                                        {...item}
                                        key={i}
                                        index={i}
                                        handler={this.deleteHandler}/>
                        }
                        return(line);
                    }
                    )}
                <tr>
                    <td colSpan={3} style={{padding: '0px'}}>
                        <EntryWidget
                            itemList={this.state.items}
                            insertHandler={this.insertHandler}/>
                    </td>
                </tr>
                
                </tbody>
                <Totals 
                    span={3}
                    list={this.state.items}
                    subtotalReducer={this.subtotalReducer}/>
            </table>
        );
    }
}

const SaleLine = (props) =>{
    let total = props.unitPrice * parseFloat(props.quantity);
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>
                {props.quantity} x {
                    props.selected.split('-')[1]
                } @ ${props.unitPrice.toFixed(2)} each.
            </td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

const ServiceLine = (props) =>{
    let total = (parseFloat(props.hours) * parseFloat(props.rate)) +
         parseFloat(props.fee);
    return(
        <tr>
            <td>
                <DeleteButton
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{
                props.selected.split('-')[1]
            } - Flat Fee: ${props.fee} + {props.hours}Hrs x @ ${props.rate} /Hr</td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

const BillableLine = (props) =>{
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{props.description}</td>
            <td>{parseFloat(props.amount).toFixed(2)}</td>
        </tr>
    )
}

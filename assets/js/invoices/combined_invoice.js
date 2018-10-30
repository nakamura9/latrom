import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget, Totals} from '../src/common';
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

         //check if the page is an update
         let URL = window.location.href;
         let decomposed = URL.split('/');
         let tail = decomposed[decomposed.length - 1];
         
         if(tail !== 'create-combined-invoice'){
             axios({
                 url: '/invoicing/api/combined-invoice/' + tail,
                 method: 'GET',
             }).then(res =>{
                 console.log(res);
                 let itemList = res.data.combinedinvoiceline_set.map((line) =>{
                    let lineMappings = {
                        1: 'sale',
                        2: 'service',
                        3: 'billable'
                    };
                    let data;
                    if(line.line_type === 1){
                        data = {
                            item: line.item.code + '-' + line.item.item_name,
                            quantity: line.quantity_or_hours,
                            price: line.item.unit_sales_price
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
                            billable: line.expense.id + '-' +line.expense.description,
                            description: line.expense.description,
                            amount: line.expense.amount 
                        }
                    }
                    return {
                        lineType: lineMappings[line.line_type],
                        data: data
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
        if(y.lineType === 'sale'){
            let total = y.data.price * parseFloat(y.data.quantity);
            
            return (x + total);
        }else if(y.lineType === 'service'){
            let total = parseFloat((y.data.rate) * parseFloat(y.data.hours)) + 
                parseFloat(y.data.flatFee);
            return (x + total);
        }else{
            //billable
            return (x + parseFloat(y.data.amount));
        }
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
                    itemList={this.state.items}
                    insertHandler={this.insertHandler}/>
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
    let total = (parseFloat(props.hours) * parseFloat(props.rate)) +
         parseFloat(props.flatFee);
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

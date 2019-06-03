import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton} from '../src/common';
import EntryWidget from './invoice_entry';
import Totals from './invoice_totals';

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
                            unitPrice: parseFloat(line.product.unit_price),
                            
                        };
                    }else if (line.line_type === 2){
                        data = {
                            selected: line.service.id + '-' + line.service.service.name,
                            hours: line.service.hours,
                            rate: line.service.hourly_rate,
                            fee: line.service.flat_fee
                        }
                    }else if (line.line_type === 3){
                        data = {
                            selected: line.expense.id + '-' +line.expense.expense.description,
                            description: line.expense.expense.description,
                            amount: line.expense.expense.amount 
                        }
                    }
                    return {
                        type: lineMappings[line.line_type],
                        ...data,
                        discount: parseFloat(line.discount),
                        tax: line.tax.id +'-'+line.tax.name +
                                    '@'+line.tax.rate
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
                        <th style={{width:"45%"}}>Description</th>
                        <th style={{width:"15%"}}>Discount</th>
                        <th style={{width:"15%"}}>Tax</th>
                        <th style={{width:"15%"}}>Line Total</th>
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
                    <td colSpan={5} style={{padding: '0px'}}>
                        <EntryWidget
                            itemList={this.state.items}
                            insertHandler={this.insertHandler}/>
                    </td>
                </tr>
                
                </tbody>
                <Totals list={this.state.items}/>
            
                </table>

        );
    }
}

const SaleLine = (props) =>{
    const subtotal = props.unitPrice * parseFloat(props.quantity);
    const discount =  subtotal * (props.discount / 100.0)
    const taxRate = parseFloat(props.tax.split('@')[1])
    const tax = (subtotal - discount) * (taxRate /100.0) 
    const total = subtotal - discount + tax
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
                } @ ${parseFloat(props.unitPrice).toFixed(2)} each.
            </td>
            <td>{props.discount}</td>
            <td>{props.tax}%</td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

const ServiceLine = (props) =>{
    console.log('tax')
    console.log(props.tax)
    const subtotal = (parseFloat(props.hours) * parseFloat(props.rate)) +
         parseFloat(props.fee);
    const discount =  subtotal * (props.discount / 100.0)
    const taxRate = parseFloat(props.tax.split('@')[1])
    const tax = (subtotal - discount) * (taxRate /100.0) 
    const total = subtotal - discount + tax

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
            <td>{props.discount}</td>
            <td>{props.tax}%</td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

const BillableLine = (props) =>{
    const subtotal  =parseFloat(props.amount);
    const discount =  subtotal * (props.discount / 100.0)
    const taxRate = parseFloat(props.tax.split('@')[1])
    const tax = (subtotal - discount) * (taxRate /100.0) 
    const total = subtotal - discount + tax
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{props.description} @ ${props.amount}</td>
            <td>{props.discount}</td>
            <td>{props.tax}%</td>
            <td>{total.toFixed(2)}</td>
        </tr>
    )
}

import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget} from '../src/common';

export default class BillTable extends Component{
    
    state = {
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
    addExpense = (expense) => {
        var decomposed = expense.split('-');
        var pk = decomposed[0];
        var name = decomposed[1];
        axios({
            url: '/accounting/api/expense/' + pk,
            method: 'GET'
        }).then(res => {
            let newItems = this.state.items;
            newItems.push({
                pk: pk,
                name: name,
                amount: res.data.amount
            });
            this.setState({'items': newItems});
            this.updateForm();
        });
    }

    removeExpense = (id) => {
        let newItems = this.state.items;
        newItems.splice(id, 1);
        this.setState({'items': newItems});
        this.updateForm()
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
                        <th style={{width:"70%"}}>Expense</th>
                        <th style={{width:"20%"}}>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.items.map((item, i) =>(
                        <tr key={i}>
                            <td>
                                <DeleteButton 
                                    handler={this.removeExpense}
                                    index={i} />
                            </td>
                            <td>{item.name}</td>
                            <td>{item.amount}</td>
                        </tr>
                    ))}
                <EntryRow addExpense={this.addExpense.bind(this)}/>
                </tbody>
                <tfoot>
                    <tr>
                        <th colSpan={2}>Total</th>
                        <td>{this.state.total}</td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}

class EntryRow extends Component{
    state = {
        items: [],
        selected: ''
    }

    componentDidMount(){
        document.getElementById('id_customer').addEventListener(
            'change', this.setCustomer.bind(this))
    }

    setCustomer = (evt) => {
        var customer = evt.target.value;
        axios({
            url: '/invoicing/api/customer/' + customer,
            method: 'GET'
        }).then(res => {;
            this.setState({'items': res.data.expense_set});
        })
    }

    clickHandler = () => {
        this.props.addExpense(this.state.selected);
    }

    inputHandler = (evt) => {
        this.setState({'selected': evt.target.value});
    }
    
    render(){
        var hasBillables =<tr>
        <td colSpan={2}>      
            <input type="text"
                className="form-control"
                list="expense-datalist"
                onChange={this.inputHandler.bind(this)}
                />
                <datalist id="expense-datalist">
                    {this.state.items.map((item, i) =>(
                        <option key={i}>{item.id + '-' + item.description}</option>
                    ))}
                    
                </datalist>

        </td>
        <td>
            <button 
                className="btn btn-secondary"
                onClick={this.clickHandler.bind(this)}
                type="button">
                    Insert
            </button>
        </td>
    </tr> 
        var hasNoBillables = <tr>
        <td colSpan={3}>The selected customer has no billables</td>
      </tr> 
        return(
            this.state.items.length === 0 ? hasNoBillables : hasBillables
        );
    }
}
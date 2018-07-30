import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget} from '../src/common';

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
                        <th style={{width:"70%"}}>Description</th>
                        <th style={{width:"20%"}}>Line Total</th>
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

class EntryRow extends Component{
    state = {
        selectedLineType: ''
    }
    handleRadioChange = (evt) => {
        this.setState({selectedLineType: evt.target.value})
    }
    render(){
        let renderedForm;
        if(this.state.selectedLineType === 'sale'){
            renderedForm = (
                <tr>
                    <td>
                        <input 
                            type="text" 
                            placeholder="Select Product..."
                            className="form-control"/>
                    </td>
                    <td>
                        <input 
                            type="text"
                            placeholder="Quantity..."
                            className="form-control"/>
                    </td>
                    <td>
                        <button className="btn btn-primary">Insert</button>
                    </td>
                </tr>
            );
        }else if(this.state.selectedLineType === 'service'){
            renderedForm = (
                <tr>
                    <td>
                        <input 
                            type="text" 
                            placeholder="Select Service..."
                            className="form-control"/>
                    </td>
                    <td>
                        <input 
                            type="text"
                            placeholder="Hours..."
                            className="form-control"/>
                    </td>
                    <td>
                        <button className="btn btn-primary">Insert</button>
                    </td>
                </tr>
            );
        }else if(this.state.selectedLineType === "billable"){
            //billable
            renderedForm = (
                <tr>
                    <td colSpan={2}>
                        <input 
                            type="text" 
                            placeholder="Select Billable Expense..."
                            className="form-control"/>
                    </td>
                    <td>
                        <button className="btn btn-primary">Insert</button>
                    </td>
                </tr>
            );            
        }else{
            renderedForm = (
                <tr>
                    <th colSpan={3}>
                        Select a Line type
                    </th>
                </tr>)
        }
        return(
                <tr>
                    <td colSpan={3}>
                        <h3>Invoice Lines</h3>
                        <h6>Choose between a product sale, service or billable expense and enter the appropriate details</h6>
                        <hr />
                        <div >
                            <label 
                                className="radio-inline" 
                                style={{marginLeft: "30px"}}>
                                <input 
                                    type="radio" 
                                    name="line_type"
                                    value="sale"
                                    onChange={this.handleRadioChange} />Sale
                            </label>
                            <label 
                                className="radio-inline" 
                                style={{marginLeft: "30px"}}>
                                <input 
                                    type="radio" 
                                    name="line_type"
                                    value="service"
                                    onChange={this.handleRadioChange} />Service
                            </label>
                            <label 
                                className="radio-inline" 
                                style={{marginLeft: "30px"}}>
                                <input 
                                    type="radio" 
                                    name="line_type"
                                    value="billable"
                                    onChange={this.handleRadioChange} />Billable
                            </label>
                        </div>
                        <div>
                            {renderedForm}
                        </div>
                    </td>
                </tr>
            
        );
    }
}
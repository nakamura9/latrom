import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import {SearchableWidget, DeleteButton} from '../src/common';

let PK = $('#id_source_warehouse').val();

export default class TransferItems extends Component{
    constructor(props){
        super(props);
        this.state = {
            lines: []
        }
    }

    componentDidMount(){
        $('<input>').attr({
            type: 'hidden',
            value: '',
            name: 'items',
            id:'id_items'
        }).appendTo('form');
    }

    removeHandler = (index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, this.updateForm);
    }

    insertHandler = (data) =>{
        let newLines = [...this.state.lines];
        newLines.push(data)
        this.setState({lines: newLines}, this.updateForm);
    }
    updateForm =() =>{
        $('#id_items').val(
            encodeURIComponent(
                JSON.stringify(this.state.lines)
            )
        );
    }

    render(){
        return(
            <table className="table">
    <thead>
        <tr className="bg-primary">
            <th>Item</th>
            <th>Quantity</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
        {this.state.lines.map((line, i) =>(
            <TransferLine 
                data={line} 
                key={i}
                index={i}
                removeHandler={this.removeHandler}/>
            ))}
    </tbody>
    <tfoot>
            <EntryRow 
                insertHandler={this.insertHandler}/>
    </tfoot>
</table>
        );
    }
}

class TransferLine extends Component{
    render(){
        return(
            <tr>
                <td>{this.props.data.item}</td>
                <td>{this.props.data.quantity}</td>
                
                <td>
                    <DeleteButton 
                        index={this.props.index}
                        handler={this.props.removeHandler}/>
                </td>
        </tr>
        );
    }
}


class EntryRow extends Component{
    state ={
        item: "",
        quantity: ""
    }
    onSelectItem = (data) =>{
        this.setState({item: data});
    }

    onClearItem = () =>{
        this.setState({item: ""});
    }
    onSetQuantity = (evt) =>{
        this.setState({quantity: evt.target.value});
    }

    render(){
        return(
            <tr>
                <td>
                    <SearchableWidget 
                        dataURL={
                            '/inventory/api/unpaginated-warehouse-items/' + PK
                        }
                        displayField="name"
                        idField="id"
                        onSelect={this.onSelectItem}
                        onClear={this.onClearItem}/>
                </td>
            <td>
                <input type="number" 
                    className="form-control"
                    name="quantity"
                    onChange={this.onSetQuantity}/>
            </td>
            <td>
                    <button className="btn btn-primary"
                        onClick={() => this.props.insertHandler(this.state)}>Add Item</button>
            </td>
        </tr>
        )
    }
}
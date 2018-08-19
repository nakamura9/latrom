import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget} from '../src/common';
import $ from 'jquery';


class ScrappingTable extends Component{
    state = {
        lines : [],
        totalValue: 0.0
    }

    componentDidMount(){
        $('<input>').attr({
            type:'hidden',
            name:'items',
            value: '',
            id: 'id_items'
        }).appendTo('form');
    }

    addItemHandler = (data) => {
        let newLines = [...this.state.lines];
        //get value data
        axios({
            url: '/inventory/api/product/' + data.pk,
            method: 'GET'
        }).then( res =>{
            let total = res.data.unit_sales_price * data.quantity
            newLines.push({
                ...data, 
                total: total
            });
            this.setState({lines: newLines}, () => {
                this.updateTotals();
                this.updateForm();
            });
        });
         
    }

    removeItemHandler =(index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, () => {
            this.updateTotals();
            this.updateForm();
        });
        
    }

    updateTotals = () =>{
        let total = this.state.lines.reduce((a, b) => {
            return(a + b.total);
        }, 0);
        this.setState({totalValue: total})
    }

    updateForm = () =>{
        $('#id_items').val(
            encodeURIComponent(JSON.stringify(
                this.state.lines
            ))
        );
    }

    render(){
        let cellStyle = {
            padding:'15px',
            color:'white',
            backgroundColor:'black'
        }
        return(
            <table>
                <thead>
                    <tr>
                        <th style={{
                            width:'10%',
                            ...cellStyle
                        }}></th>
                        <th style={{
                            width:'20%',
                            ...cellStyle
                        }}>Item</th>
                        <th style={{
                            width:'10%',
                            ...cellStyle
                            }}>Quantity</th>
                        <th style={{
                            width:'50%',
                            ...cellStyle
                        }}>ScrappingNote</th>
                        <th style={{
                            width:'10%',
                            ...cellStyle
                        }}>Value</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.lines.map((line, i) => {
                        return(<ScrappingLine 
                                    data={line}
                                    key={i}
                                    index={i}
                                    handler={this.removeItemHandler}/>);
                    })}
                <ScrappingEntry 
                    insertHandler={this.addItemHandler}/>
                </tbody>
                
                <tfoot>
                    <tr>
                        <th colSpan={4}>Total</th>
                        <td>{this.state.totalValue.toFixed(2)}</td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}

const ScrappingLine = (props) => {
    return(
        <tr>
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.handler}/>
            </td>
            <td>{props.data.name}</td>
            <td>{props.data.quantity}</td>
            <td>{props.data.note}</td>
            <td>{props.data.total.toFixed(2)}</td>
        </tr>
    )
}

class ScrappingEntry extends Component{
    state = {
        items : [],
        inputs: {
            name: "",
            pk: "",
            quantity: 0,
            note: "",
            total: 0
        }
    }

    selectHandler = (val) =>{
        let newInputs = {...this.state.inputs};
        let pk;
        let name;
        [pk, name] = val.split('-');
        newInputs['name'] = name;
        newInputs['pk'] = pk;
        this.setState({inputs:newInputs});
        }

    clearHandler = () =>{
            let newInputs = {...this.state.inputs};
            newInputs['name'] = "";
            newInputs['pk'] = "";
            this.setState({inputs:newInputs});
        }
    
    onInputChange = (event) =>{
        let name = event.target.name;
        let newInputs = {...this.state.inputs};
        newInputs[name] = event.target.value;
        this.setState({inputs: newInputs});
    }

    submitHandler = () => {
        this.props.insertHandler(this.state.inputs);
        this.setState({inputs: {
                quantity: 0,
                note: "",
                name: "",
                pk: "",
                total: 0
            }});
    }
    render(){
        return(
            <tr>
                <td colSpan={2}>
                    <SearchableWidget 
                        dataURL="/inventory/api/product"
                        displayField="name"
                        onSelect={this.selectHandler}
                        onClear={this.clearHandler}
                        idField="id"/>
                </td>
                <td>
                    <input 
                        name="quantity"    
                        type="number"
                        className="form-control"
                        onChange={this.onInputChange}
                        value={this.state.inputs.quantity}/>
                </td>
                <td>
                    <input 
                    name="note"    
                    type="text"
                    className="form-control"
                    onChange={this.onInputChange}
                    value={this.state.inputs.note}/>
                </td>
                <td>
                    <button 
                        className="btn btn-primary"
                        onClick={this.submitHandler}>
                        Insert
                    </button>
                </td>
            </tr>
        );
    }
}

export default ScrappingTable;
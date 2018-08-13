import React, {Component} from 'react';
import axios from 'axios';
import {DeleteButton, SearchableWidget} from '../src/common';


class ScrappingTable extends Component{
    state = {
        lines : [],
        totalValue: 0.0
    }
    addItemHandler = (data) => {

    }

    removeItemHandler =(index) =>{

    }
    render(){
        return(
            <table>
                <thead>
                    <tr>
                        <tr style={{width:'10%'}}></tr>
                        <th style={{width:'20%'}}>Item</th>
                        <th style={{width:'10%'}}>Quantity</th>
                        <th style={{width:'50%'}}>ScrappingNote</th>
                        <th style={{width:'10%'}}>Value</th>
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

                </tbody>
                <ScrappingEntry />
                <tfoot>
                    <tr>
                        <th colSpan={4}>Total</th>
                        <td>{this.state.totalValue}</td>
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
            <td>{props.data.total}</td>
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
            note: ""
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

    render(){
        return(
            <tr>
                <td colSpan={2}>
                    <SearchableWidget 
                        dataURL="/inventory/api/item"
                        displayField="item_name"
                        onSelect={this.selectHandler}
                        onClear={this.clearHandler}
                        idField="code"/>
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
                        onClick={() => 
                            this.props.insertHandler(this.state.inputs)}>
                        Insert
                    </button>
                </td>
            </tr>
        );
    }
}

export default ScrappingTable;
import React, {Component} from 'react';
import {SearchableWidget, AsyncSelect, DeleteButton} from '../../src/common';
import $ from 'jquery';

class ConsumableRequisitionTable extends Component{
    state = {
        lines: []
    }

    componentDidMount = () => {
        $('<input>').attr({
            type: 'hidden',
            name: 'consumables',
            id: 'id_consumables',
            value: encodeURIComponent(JSON.stringify([]))
        }).appendTo('form');
    }
    

    insertHandler = (data) =>{
        let newLines = [...this.state.lines];
        newLines.push(data);
        this.setState({lines: newLines}, this.updateForm)
    }
    removeHandler = (index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, this.updateForm);
    }

    updateForm = () =>{
        $('#id_consumables').val(encodeURIComponent(
            JSON.stringify(this.state.lines)));
    }

    render(){
        const cellStyle = {
            padding:"8px",
            borderRight: "1px solid white",

        }
        return(
            <table className="table">
                <thead>
                    <tr className="bg-primary">
                        <th></th>
                        <th style={{...cellStyle ,width:"50%"}}>Item</th>
                        <th style={{...cellStyle ,width:"30%"}}>Unit</th>
                        <th style={{...cellStyle ,width:"20%"}}>Quantity</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.lines.map((line, i) => {
                        return(<RequisitionLine 
                                    key={i}
                                    data={line}
                                    handler={this.removeHandler}
                                    index={i}
                                    />)
                    })}
                </tbody>
                <RequisitionTableEntry 
                    itemList={this.state.lines}
                    insertHandler={this.insertHandler}/>
            </table>
        )
    }
}

const RequisitionLine = (props) =>{
    return(
        <tr>
            <td><DeleteButton 
                    handler={props.handler}
                    index={props.index}/></td>
            <td>{props.data.item}</td>
            <td>{props.data.unit}</td>
            <td>{props.data.quantity}</td>
        </tr>
    )
}

class RequisitionTableEntry extends Component{
    state = {
        inputs: {
            quantity: 0,
            unit: 0,
            item: ""
        }
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                inputs: {
                    quantity: 0,
                    unit: 0,
                    item: ""
                }
            })
            //remove selected choice from list of choices 
        }
    }

    inputHandler = (val, field) =>{
        let newInputs = {...this.state.inputs};
        newInputs[field] = val;
        this.setState({inputs: newInputs});
    }
    onSelectHandler = (val) =>{
        this.inputHandler(val, "item");
    }

    onClearHandler = () =>{
        this.inputHandler("", 'item');
    }

    quantityHandler = (evt) => {
        this.inputHandler(evt.target.value, "quantity");
    }

    unitHandler = (val) =>{
        this.inputHandler(val, "unit");
    }

    render(){
        return(
            <tfoot>
                <tr>
                    
                    <td colSpan={2}>
                        <SearchableWidget
                            list={this.props.itemList}
                            dataURL="/inventory/api/consumable/"
                            idField="id"
                            displayField="name"
                            onSelect={this.onSelectHandler}
                            onClear={this.onClearHandler}/>
                    </td>
                    <td>
                        <AsyncSelect 
                            dataURL='/inventory/api/unit/'
                            resProcessor={(res) => {
                                return res.data.map((unit) =>({
                                    value: unit.id,
                                    name: unit.name
                                }))
                            }}
                            handler={this.unitHandler}/>
                    </td>
                    <td>
                        <input 
                            className="form-control"
                            name="quantity"
                            type="number"
                            value={this.state.inputs.quantity}
                            onChange={this.quantityHandler}/>
                    </td>
                </tr>
                <tr>
                    <td colSpan={3}></td>
                    <td>
                        <button 
                            type="button"
                            className="btn btn-primary"
                            onClick={() => 
                                this.props.insertHandler(this.state.inputs)}>
                                Insert</button>
                    </td>
                </tr>
            </tfoot>
        )
    }
}

export default ConsumableRequisitionTable;
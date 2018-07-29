import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class TransferItems extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
            lines: [],
            inputs: {
                item: "",
                quantity: ""
            }
        }
    }

    componentDidMount(){
        document.getElementById('id_source_warehouse').addEventListener(
            'change', this.getItems.bind(this)
        );
        $('<input>').attr({
            type: 'hidden',
            value: '',
            name: 'items',
            id:'id_items',                }).appendTo('form');
    }

    getItems(evt){
        $.ajax({
            'url': '/inventory/api/unpaginated-warehouse-items/' + evt.target.value,
            'method': 'GET'
        }).then(res => {
            this.setState({items: res})
        });
        }


    getWarehouseItem(pk){
        $.ajax({
            url: '/inventory/api/warehouse-item/' + pk,
            method: 'GET'
        }).then(res => {
            this.setState({currItem: res});
        });
    }
    addItem(){
        
        if (this.state.inputs.item === "" || this.state.inputs.quantity === ""){
            alert('Please enter the necessary fields');
        }else{
            let pk = this.state.inputs.item.split('-')[0];
            
            $.ajax({
                url: '/inventory/api/warehouse-item/' + pk,
                method: 'GET'
            }).then(res => {
                if(parseFloat(this.state.inputs.quantity) > res.quantity){
                    alert('The selected warehouse does not have this quantity of items available for transfer. Number available: ' + res.quantity);
                }else{
                    
                //create table row
                let newLines = this.state.lines;
                newLines.push(this.state.inputs);
                this.setState({lines: newLines});
    
                //update hidden input
                $("#id_items").val(encodeURIComponent(
                            JSON.stringify({items: this.state.lines})));
            }
            })   
        }
    }
    removeHandler(){
        alert('removed');
    }

    handleInputChange(evt){
        let name = evt.target.name;
        let newInputs = this.state.inputs;
        newInputs[name] = evt.target.value;
        this.setState({newInputs: newInputs});
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
        {
            this.state.items.length === 0
            ?(<tr>
                <td colSpan={3}><b>Select a warehouse.</b></td>
            </tr>)
            : (<tr>
                    <td>
                        <input type="text" 
                            className="form-control"
                            list="item-list"
                            name="item"
                            onChange={this.handleInputChange.bind(this)}
                            />
                        <datalist id='item-list'>
                            {this.state.items.map((item, i) =>(
                                <option key={i}
                                    value={item.id + "-" + item.item.item_name} />
                            ))}
                        </datalist>
                    </td>
                    <td>
                        <input type="number" 
                            className="form-control"
                            name="quantity"
                            onChange={this.handleInputChange.bind(this)}/>
                    </td>
                    <td>
                            <button className="btn btn-primary"
                                onClick={this.addItem.bind(this)}>Add Item</button>
                    </td>
        </tr>)
        }
        
    </thead>
    <tbody>
            {this.state.lines.map((line, i) =>(
                <TransferLine data={line} key={i}
                    removeHandler={this.removeHandler.bind(this)}/>
            )) }
    </tbody>
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
                    <button className="btn btn-danger"
                        onClick={this.props.removeHandler}>
                        <i className="fas fa-trash" ></i>
                    </button>
                </td>
        </tr>
        );
    }
}

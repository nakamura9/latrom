import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class SalesInvoiceForm extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
            subtotal: 0.0,
            tax: 0.0,
            taxRate: 0.0,
            total: 0.0
        }
    }
    addItem(data){
        data['subtotal'] = data.quantity * data.unit_price;
        let newItems = this.state.items;
        newItems.push(data);
        this.setState({items:newItems});
        this.updateList();
    }

    removeItem(index){
        let newItems = this.state.items;
        newItems.splice(index, 1);
        this.setState({items: newItems});
        this.updateList();
    }
    
    updateList(){
        $('#id_item_list').val(encodeURIComponent(JSON.stringify(
            this.state.items
        )));
        var subtotal = this.state.items.reduce((x,y) =>(
            x + y.subtotal
        ), 0);
        var taxAmount;
        if(this.state.taxRate){
            taxAmount = subtotal * (this.state.taxRate.rate / 100);
        }else{
            taxAmount = 0.0;
        }
        var total = subtotal + taxAmount;
        this.setState({
            subtotal : subtotal,
            tax : taxAmount,
            total : total
        });
    }

    componentDidMount(){
        $('<input>').attr({
            'type': 'hidden',
            'value': '',
            'name': 'item_list',
            'id': 'id_item_list'
        }).appendTo('form');
        // get config
        $.ajax({
            'url': '/invoicing/api/config/1',
            'method': 'GET'
        }).then(
            res => {
                this.setState({taxRate: res.sales_tax});
            }
        );
    }

    render(){
        let theadStyle = {
            padding: '2mm',
            borderRight: '1px solid white',
            color: 'white',
            backgroundColor: 'black'
        };
        return(
            <table className="table">
                <thead>
                    <tr style={theadStyle}>
                        <th></th>
                        <th>Item</th>
                        <th>Unit Price</th>
                        <th>Quantity</th>
                        <th>Line total</th>
                    </tr>
                </thead>
                <tbody>
                    { this.state.items.map((item, i) => (
                    <tr key={i}>
                        <td>
                            <button className="btn btn-danger"
                                onClick={() => (this.removeItem(i))}>
                                <i className="fas fa-trash"></i>
                            </button>
                        </td>
                        <td>{item.item_name}</td>
                        <td>{item.unit_price.toFixed(2)}</td>
                        <td>{item.quantity}</td>
                        <td>{item.subtotal.toFixed(2)}</td>
                    </tr>
                    ))}
                    <EntryRow addItem={this.addItem.bind(this)}/>
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan={4} ><b>Subtotal</b></td>
                        <td >{this.state.subtotal.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td colSpan={4}><b>Tax</b></td>
                        <td>{this.state.tax.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td colSpan={4}><b>Total</b></td>
                        <td>{this.state.total.toFixed(2)}</td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}

class EntryRow extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
            inputs: {
                unit_price:0.0
            }
        };   
    }
    componentDidMount(){
        $.ajax({
            url: '/inventory/api/item/',
            method: 'GET'
        }).then(res =>{
            this.setState({items: res});
        });
    }
    inputHandler(evt){
        let name = evt.target.name;
        let newInputs = this.state.inputs;
        newInputs[name] = evt.target.value;
        this.setState({inputs: newInputs});
        if(name==="item_name"){
            var decomposed = evt.target.value.split('-');
            var pk = decomposed[0];
            $.ajax({
                url: '/inventory/api/item/' + pk,
                method:'get'
            }).then(res => {
                let newInputs = this.state.inputs;
                newInputs['unit_price'] = res.unit_sales_price
                ;
                this.setState({inputs: newInputs});
            });
        }
        
    }
    clickHandler(){
        this.props.addItem(this.state.inputs);
    }
    render(){
        return(
            <tr>
                <td colSpan={2}>
                    <input type="text" list="item-datalist"
                        name="item_name"
                        className="form-control"
                        placeholder="Select item..."
                        onChange={this.inputHandler.bind(this)}/>
                    <datalist id="item-datalist">
                    {this.state.items.map((item, i) =>(
                        <option key={i}>
                            {item.code + "-" + item.item_name}
                        </option>
                    ))}    
                    </datalist>
                </td>
                <td>{this.state.inputs.unit_price.toFixed(2)}</td>
                <td>
                    <input type="number" name="quantity"
                    onChange={this.inputHandler.bind(this)}
                    className="form-control"
                    placeholder="Quantity..." />
                </td>
                <td>
                    <button className="btn btn-primary"
                        onClick={this.clickHandler.bind(this)}>
                        Insert
                    </button>
                </td>
            </tr>
                );
    }
}
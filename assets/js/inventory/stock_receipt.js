import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class ItemReceiptTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            'populated': false,
            'items': [],
            'values': {}
        }
    }
    componentDidMount(){
        let order = document.getElementById('id_order').value;
        this.populate(order)
        $('<input>').attr({
            'name': 'received-items',
            'type': 'hidden',
            'value': '',
            'id': 'id-received-items'
        }).appendTo('form');
    }

    inputHandler(evt){
        let newVals = this.state.values;
        newVals[evt.target.name] = evt.target.value;
        this.setState({values: newVals});
        let inputVal = encodeURIComponent(
            JSON.stringify(this.state.values)
        );
        $('#id-received-items').val(inputVal);
        
    }
    
    populate = (order) =>{
        $.ajax({
            url: '/inventory/api/order/' + order,
            'method': 'GET'
        }).then(
            res => {
                this.setState({
                    'items': res.orderitem_set
                });
            }
        );
        this.setState({'populated': true});
    }
    render(){
        return(
            <table className="table">
                <thead>
                    <tr className="bg-primary text-white">
                        <th>Item Name</th>
                        <th>Ordered Quantity</th>
                        <th>Quantity Already Received</th>
                        <th>Quantity</th>
                    </tr>
                </thead>
                <Content items={this.state.items}
                    populated={this.state.populated}
                    handleInputChange={this.inputHandler.bind(this)} />
            </table>
        );
    }
}

class Content extends Component {
    

    render(){
        if(this.props.populated === false){
            return(<tbody>
                <tr>
                    <td colSpan="4">
                        <center>No Order Loaded, select an order</center>
                    </td>
                  </tr>             
                </tbody>);
        }else{
            return(<tbody>
            {this.props.items.map((item, i) => (
                <tr key={i}>
                    <td>{item.item.item_name}</td>
                    <td>{item.quantity}</td>
                    <td>{item.received}</td>
                    <td><input type="number" 
                        name={"item-" + item.id}
                        defaultValue="0.0"
                        className="form-control"
                        onChange={this.props.handleInputChange} /></td>
                </tr>
            ))}
            </tbody>)
        }
    }
}


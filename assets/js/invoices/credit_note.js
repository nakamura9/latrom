import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class CreditNoteTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            elements : [],
            credit: {}
        }
    }
    componentDidMount() {
        var invoiceNode = ReactDOM.findDOMNode(
            document.getElementById('id_invoice'));
        invoiceNode.addEventListener('change', this.populate.bind(this))
        $('<input>').attr({
            'name': 'returned-items',
            'type': 'hidden',
            'value': '',
            'id': 'id-returned-items'
        }).appendTo('form');
    }
    populate(evt){
        $.ajax({
            url: '/invoicing/api/invoice/' + evt.target.value,
            data: {},
            method: 'GET'
        }).then(res => {
            let credits = {};
            var i = 0;
            for( i in res.invoiceitem_set){
                credits[res.invoiceitem_set[i].id] = 0.0;
            }
            this.setState({
                elements: res.invoiceitem_set,
                credit: credits
            });
            
        });
    }
    
    handleInputChange(data){
        let newCreditValues = this.state.credit;
        newCreditValues[data.id] = data.returned;
        this.setState({
            credit: newCreditValues
        });
        let inputVal = encodeURIComponent(
            JSON.stringify(this.state.credit));
        $('#id-returned-items').val(inputVal);
    }
    
    render(){
        return(
            <table className="table">
                <thead className="bg-primary text-white">
                    <tr>
                    <th>Ordered Qty</th>
                    <th>Description</th>
                    <th>Price</th>
                    <th>Returned</th>
                    <th>Credit</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.elements.map((element, i) =>(
                        <CreditNoteLine key={i} 
                            element={element}
                            returnHandler={this.handleInputChange.bind(this)} />
                        
                    ))}
                    
                </tbody>
            </table>
        )
    }
}

class CreditNoteLine extends Component{
    constructor(props){
        super(props);
        this.state = {
            credit: 0.0,
            returned: 0.0,
            id: ""
        }
    }
    handleInputChange(evt){
        let credit = this.props.element.price * evt.target.value;
        this.setState({
            returned: evt.target.value,
            id: this.props.element.id,
            credit: credit
        }, () => {
            this.props.returnHandler(this.state)
        });
        
    }
    render(){
        return(
        <tr>
            <td>{this.props.element.quantity}</td>
            <td>{this.props.element.item.item_name}</td>
            <td>{this.props.element.price}</td>
            <td>
                <input type="number" 
                    name = {this.props.element.id}
                    onChange={this.handleInputChange.bind(this)}
                    className="form-control"/>
            </td>
            <td>{this.state.credit}</td>
        </tr>);
    }
}
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import AsyncSelect from './async_select';
import $ from 'jquery';

class Totals extends Component{
    state = {
        taxObj: null,
        tax: 0.00,
        subtotal: 0.00,
        total: 0.00
    }

    handleTaxChange = (id) =>{
        axios.get('/accounting/api/tax/' + id)
            .then(res => {
                this.setState({taxObj: res.data});
                $(`#${this.props.taxFormField}`).val(id);
            })
    }

    calculateTax = () =>{
        let subtotal = this.props.list.reduce(this.props.subtotalReducer, 0);
            
        let taxAmount;
        if(this.state.taxObj){
            taxAmount = subtotal * (this.state.taxObj.rate / 100);
        }else{
            taxAmount = 0.0;
        }
        let total = subtotal + taxAmount;
        this.setState({
            subtotal : subtotal,
            tax : taxAmount,
            total : total
        });
    }

    componentDidUpdate(prevProps, prevState){
        if(prevProps.list !== this.props.list){
            //update totals 
           this.calculateTax(); 
        }if(prevState.taxObj !== this.state.taxObj){
            this.calculateTax();
        }
    }

    render(){
        let contents;
        const cellStyle = {
            padding: '10px'
        }
        if(this.state.tax === null){
            contents = (
                <tfoot>
                    <tr className="bg-primary text-white">
                        <th style={cellStyle} colSpan={this.props.span - 1}>Total</th>
                        <td style={cellStyle}>{this.state.total}</td>
                    </tr>
                </tfoot>
            )
        }else{
            contents = (
                <tfoot>    
                    <tr className="bg-primary text-white">
                        <th style={cellStyle} colSpan={this.props.span - 1}>Subtotal</th>
                        <td style={cellStyle}>{this.state.subtotal.toFixed(2)}</td>
                    </tr>
                    <tr className="bg-primary text-white">
                        <th style={cellStyle} colSpan={this.props.span - 2}>Tax</th>
                        <td>
                            <AsyncSelect
                                dataURL="/accounting/api/tax/"
                                resProcessor={(res) => {
                                    return(res.data.map((tax) =>({
                                        value: tax.id,
                                        name: tax.name
                                    })))
                                }}
                                handler={this.handleTaxChange} />
                        </td>
                        <td style={cellStyle}>{this.state.tax.toFixed(2)}</td>
                    </tr>
                    <tr className="bg-primary text-white">
                        <th style={cellStyle} colSpan={this.props.span - 1}>Total</th>
                        <td style={cellStyle}>{this.state.total.toFixed(2)}</td>
                    </tr>
                </tfoot>
                )
        }
        return(contents);
    }
}

Totals.propTypes = {
    span: PropTypes.number.isRequired,
    list: PropTypes.array.isRequired,
    subtotalReducer: PropTypes.func.isRequired
}

export default Totals;
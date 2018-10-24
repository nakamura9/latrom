import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';


class Totals extends Component{
    state = {
        taxObj: null,
        tax: 0.00,
        subtotal: 0.00,
        total: 0.00
    }
    componentDidMount(){
        //get sales tax
        axios({
            method: "GET",
            url: "/invoicing/api/config/1"
        }).then(res =>{
            this.setState({taxObj: res.data.sales_tax})
        })
    }
    componentDidUpdate(prevProps, prevState){
        if(prevProps.list !== this.props.list){
            //update totals 
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
    }
    render(){
        let contents;
        if(this.state.tax === null){
            contents = (
                <tfoot>
                    <tr>
                        <th colSpan={this.props.span - 1}>Total</th>
                        <td>{this.state.total}</td>
                    </tr>
                </tfoot>
            )
        }else{
            contents = (
                <tfoot>    
                    <tr>
                            <th colSpan={this.props.span - 1}>Subtotal</th>
                            <td>{this.state.subtotal.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Tax</th>
                            <td>{this.state.tax.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Total</th>
                            <td>{this.state.total.toFixed(2)}</td>
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
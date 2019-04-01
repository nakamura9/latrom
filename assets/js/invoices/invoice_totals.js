import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import $ from 'jquery';

export const Aux = (props) => props.children;


class Totals extends Component{
    state = {
        tax: 0.00,
        subtotal: 0.00,
        total: 0.00
    }


    listMapper = (item) =>{
        let subtotal;
        if(item.type === 'product'){
            subtotal = item.unitPrice * parseFloat(item.quantity);
            
        }else if(item.type === 'service'){
            subtotal = (parseFloat(item.hours) * parseFloat(item.rate)) +
                parseFloat(item.fee);
            
        }else{
            //billable
            subtotal  =parseFloat(item.amount);
            
        }
        
        const discount =  subtotal * (item.discount / 100.0)
        subtotal = subtotal - discount;
        const percentage = parseFloat(item.tax.split('@')[1])
        const tax = subtotal * (percentage /100.0)
        return ({
            subtotal: subtotal,
            tax: tax
        });
    }
    subtotalReducer =(x, y) =>{
        return x + y.subtotal
    }

    taxReducer = (x, y) =>{
        return x + y.tax;
    }

    componentDidUpdate(prevProps, prevState){
        if(prevProps.list !== this.props.list || prevState.taxObj !== this.state.taxObj){
            //update totals 
            const mappedList = this.props.list.map(this.listMapper)
            let subtotal = mappedList.reduce(this.subtotalReducer, 0);
            let tax = mappedList.reduce(this.taxReducer, 0)            

            let total = subtotal + tax;
            this.setState({
                subtotal : subtotal,
                tax : tax,
                total : total
            });
        }
    }
    render(){
        return(
            <tfoot>    
                <tr>
                        <th colSpan={4}>Subtotal</th>
                        <td>{this.state.subtotal.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <th colSpan={4}>Tax</th>
                        <td>{this.state.tax.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <th colSpan={4}>Total</th>
                        <td>{this.state.total.toFixed(2)}</td>
                    </tr>
            </tfoot>
            );
    }
}
export default Totals;
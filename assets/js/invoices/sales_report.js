import React, {Component} from 'react';
import MultipleSelectWidget from '../src/multiple_select/containers/root';

class SaleReportModifiers extends Component{
    render(){
        return (<div>
            <p>Filter By Sales Representative:</p>
            <MultipleSelectWidget 
                inputField="reps"
                idField="number"
                dataURL="/invoicing/api/sales-rep"
                nameField="rep_name"/>
            <p>Filter By Customers:</p>
            <MultipleSelectWidget 
                inputField="customers"
                dataURL="/invoicing/api/customer"
                nameField="name" />
            <p>Filter By Products:</p>
            <MultipleSelectWidget 
                inputField="products"
                dataURL="/inventory/api/product"
                nameField="name" />
            <p>Filter by Services:</p>
            <MultipleSelectWidget 
                inputField="services"
                dataURL="/services/api/service"
                nameField="name" />
        </div>)
    }
}

export default SaleReportModifiers;
import React, {Component} from 'react';
import $ from 'jquery';
import {Heading, TableContent} from '../src/base_table';

class InvoiceTable extends Component{
    constructor(props){
        super(props);
        /*
        No props
        State consists of the running total of the table and a list of items
        parent component for the rows and the item form 
        child of the overall form component */
        this.state = {
            total: 0,
            items: [],
            tax_rate: 0,
            tax_amount:0,
            subtotal: 0,
        };
    }

    componentDidMount(){
        if(this.props.populated){
            //get the id of the current invoice
            var url = window.location.href;
            var url_elements = url.split("/");
            var pk = url_elements[url_elements.length-1];
            var typ = url_elements[url_elements.length-2];
            //request its data from the api
            $.ajax({
                url: this.props.url + pk +"/",
                method: "GET",
                data: {}
            }).then(res => {
                if(typ === 'quote-update'){
                    var items = res.quoteitem_set;
                }else{
                    var items = res.invoiceitem_set;
                }
                var i=0;
                for(i in items){
                    var subtotal = items[i].item.unit_sales_price * 
                        items[i].quantity;
                    this.setState({
                            items: this.state.items.concat({
                                code: items[i].item.code,
                                description: items[i].item.item_name,
                                price: items[i].item.unit_sales_price,
                                quantity: items[i].quantity,
                                discount: items[i].discount,
                                subtotal: subtotal,
                                id: items[i].id
                        })
                    });
                }
            });
        }   
    }
    
    removeItem(index){
        //removes an item from the state and the table
        
        var newState = this.state;
        
        if ($("#item_" + index)){
            this.props.removeHandler(index);
        }
        // dont use else statement!
        if(this.props.populated){
            var pk = this.state.items[index].id;
            this.props.populatedRemoveHandler(pk);
        }
        newState.items.splice(index, 1);
        this.setState(newState);
    }

    addItem(data){
        //adds items to the state 
        this.setState({items: this.state.items.concat(data)});
        this.props.addHandler(data, this.state.items.length);
        
        //set subtotals tax amounts and tax rates
        //get tax rate
        var tax_obj = $('#id_tax').val();
        if(tax_obj === ""){
            alert('Please Select a Valid Tax Rate');
        }else{
            $.ajax({
                url: '/accounting/api/tax/' + tax_obj,
                method: 'get'
            }).then(
                res =>{
                    //get subtotal
                    var subtotal = this.state.items.reduce((x, y) => {
                        let subtotal = y.price * y.quantity;
                        let discount = subtotal * (y.discount / 100);
                        return (x + (subtotal - discount));
                    }, 0)
                    //set tax amount
                    var tax_amount = subtotal * (res.rate / 100);
                    //set total
                    var total = tax_amount + subtotal;
                    this.setState({
                        tax_rate: res.rate,
                        tax_amount: tax_amount,
                        subtotal: subtotal,
                        total:total
                    })
                }
            )
    
            
        }
        
    }

    subtotalHandler(row){
        return(row.subtotal.toFixed(2));
    }

    render(){
        const headStyle = {
            borderLeft: "1px solid white",
        };
        const field_names = ["Qty", "Description", "Unit Price",'Discount',  "Subtotal"];
        return(
            <div>
                <h3>Item Table</h3>
                <table className="table table-striped">
                    <Heading fields={field_names} />
                    <TableContent contents={this.state.items}
                        fields={["quantity", "description","price", 'discount',]} 
                        removeHandler={this.removeItem.bind(this)}
                        subtotalHandler={this.subtotalHandler}/>    
                    <EntryRow url="/inventory/api/product" 
                            addItem={this.addItem.bind(this)}
                            contents={this.state.items}
                            tax_rate={this.state.tax_rate}
                            tax_amount={this.state.tax_amount}
                            subtotal={this.state.subtotal}
                            total={this.state.total} />
                </table>
            </div>
        );
    }
}

class EntryRow extends Component {
    constructor(props){
        super(props);
        this.state = {
            inputs: {},
            options: [],
            curr_item: {
                unit_sales_price: 0.00
            },
            show_tax: false,
            curr_tax_rate: 0
        };
    }
    
    componentDidMount(){
        
        //inventory items list
        $.ajax({
            url: this.props.url,
            data: {},
            method: "GET",
        }).then(res => {
        this.setState({options: res});
        });

        //determine whether to show the tax information
        $.ajax({
            url: '/base/api/config',
            method:'get'
        }).then( res =>{
            this.setState({show_tax: res.include_tax_in_invoice});
        });

    }

    inputHandler(event){
        var name= event.target.name;
        var value = event.target.value;
        var newVals = this.state.inputs;
        newVals[name] = value;
        if(name==="item"){
            var decomposed = value.split('-');
            var pk = decomposed[0];
            $.ajax({
                url: '/inventory/api/product/' + pk,
                method:'get'
            }).then(res => {
            this.setState({curr_item: res})
            });
        }

        this.setState({inputs: newVals});
    }

    addItem(){
            var data = {};
            data.code = this.state.curr_item.code
            data.quantity = this.state.inputs.quantity;
            data.description = this.state.curr_item.item_name;
            data.discount = this.state.inputs.discount;
            data.price = this.state.curr_item.unit_sales_price;
            var total = data.price * data.quantity;
            var discount = total * data.discount / 100;
            data.subtotal = total - discount;
            this.props.addItem(data);
            // clears the unit price field
            this.setState({curr_item: {
                unit_sales_price: 0.00
            }})
        $('#entry-row-item').val("");
        $('#entry-row-quantity').val("");
        $('#entry-row-discount').val("");
        
        
    }

    render(){
        var footStyle ={
            textAlign:'right'
        }
        var inputStyle = {
            width: "100%",
            height: "100%",
        };
        return(
            <tfoot>
                <tr>
                    <td colSpan={2}>
                        <input className="form-control" 
                            placeholder="Qty"
                            id="entry-row-quantity" 
                            type="number"
                            name='quantity' 
                            onChange={this.inputHandler.bind(this)} />
                    </td>
                    <td style={{width:'40%'}}>
                        <input placeholder="Select Item..."     
                            className="form-control" 
                            id="entry-row-item" 
                            name='item'
                            type="text" list="item-datalist"  
                            onChange={this.inputHandler.bind(this)} />
                        <datalist id="item-datalist">
                    {this.state.options.map((item, index) =>( 
                        <option key={index} >{item.code} - {item.item_name} </option>
                        ))}
                    </datalist>
                    </td>
                    
                    <td>
                        {this.state.curr_item.unit_sales_price}
                    </td>
                    <td><input className="form-control" 
                        id="entry-row-discount" 
                        type="number" 
                        placeholder="Dis..."
                        name='discount'
                        onChange={this.inputHandler.bind(this)} /></td>
                    
                    <td>
                        <center>
                            <button className="btn btn-dark" onClick={this.addItem.bind(this)}>
                            Add Item
                            </button>
                        </center>
                    </td>
                </tr>
                <tr style={footStyle}>
                    <td colSpan={5}><b><u>SubTotal:</u></b></td>
                    <td><b><u>{this.props.subtotal.toFixed(2)}</u></b></td>
                </tr>
                <tr style={footStyle}>
                    <td colSpan={5}><b><u>Tax Rate:</u></b></td>
                    <td><b><u>{this.props.tax_rate}</u></b></td>
                </tr>
                <tr style={footStyle}>
                    <td colSpan={5}><b><u>Tax Due:</u></b></td>
                    <td><b><u>{this.props.tax_amount.toFixed(2)}</u></b></td>
                </tr>
                <tr style={footStyle}>
                    <td colSpan={5}><b><u>Total:</u></b></td>
                    <td><b><u>{this.props.total.toFixed(2)}</u></b></td>
                </tr>
            </tfoot>
        );
    }
}

export default InvoiceTable;
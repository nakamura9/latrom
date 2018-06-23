import React, {Component} from 'react';
import $ from 'jquery';
import {Heading, TableContent} from './base_table';

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
            items: []
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
    }

    subtotalHandler(row){
        return(row.subtotal);
    }

    render(){
        const headStyle = {
            borderLeft: "1px solid white",
        };
        const field_names = ["Item Code", "Item Description", "Quantity",'Discount', "Unit Price",  "Subtotal"];
        return(
            <div>
                <h3>Item Table</h3>
                <table className="table table-striped">
                    <Heading fields={field_names} />
                    <TableContent contents={this.state.items}
                        fields={["code", "description", "quantity",  'discount',"price",]} 
                        removeHandler={this.removeItem.bind(this)}
                        subtotalHandler={this.subtotalHandler}/>    
                    <EntryRow url="/inventory/api/item" 
                            addItem={this.addItem.bind(this)}
                            contents={this.state.items} />
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
            options: []
        };
    }
    
    componentDidMount(){
        $.ajax({
            url: this.props.url,
            data: {},
            method: "GET",
        }).then(res => {
        this.setState({options: res});
        });
    }

    inputHandler(event){
        var name= event.target.name;
        var value = event.target.value;
        var newVals = this.state.inputs;
        newVals[name] = value;
        this.setState({inputs: newVals});
    }

    addItem(){
        var decomposed = this.state.inputs.item.split("-");
        var data = {};
        data.code = decomposed[0];
        data.description = decomposed[1];
        data.price = parseFloat(decomposed[2]);
        data.quantity = this.state.inputs.quantity;
        data.discount = this.state.inputs.discount;
        var total = data.price * data.quantity
        var discount = total * data.discount / 100;
        data.subtotal = total - discount;
        this.props.addItem(data);
        $('#entry-row-item').val("");
        $('#entry-row-quantity').val("");
        $('#entry-row-discount').val("");
        
    }

    render(){
        return(
            <tfoot>
                <tr>
                    <td colSpan="4">
                        <input placeholder="Select Item..."     
                            className="form-control" 
                            id="entry-row-item" 
                            name='item'
                            type="text" list="item-datalist"  
                            onChange={this.inputHandler.bind(this)} />
                        <datalist id="item-datalist">
                    {this.state.options.map((item, index) =>( 
                        <option key={index} >{item.code} - {item.item_name} - {item.unit_sales_price}</option>
                        ))}
                    </datalist>
                    </td>
                    <td>
                        <input className="form-control" 
                            placeholder="quantity"
                            id="entry-row-quantity" 
                            type="number"
                            name='quantity' 
                            onChange={this.inputHandler.bind(this)} />
                    </td>
                    <td><input className="form-control" 
                        id="entry-row-discount" 
                        type="number" 
                        placeholder="discount"
                        name='discount'
                        onChange={this.inputHandler.bind(this)} /></td>
                    <td>
                        <center>
                            <button className="btn btn-primary" onClick={this.addItem.bind(this)}>
                            Add Item
                            </button>
                        </center>
                    </td>
                </tr>
                <tr>
                    <td colSpan={6}></td>
                    <td><b><u>Total:</u>{(this.props.contents.length === 0) ? 0 :
                                         this.props.contents.reduce(
                                             function(a,b){
                                                return a + b.subtotal
                                            }, 0
                                    )}
                    </b></td>
                </tr>
            </tfoot>
        );
    }
}

export default InvoiceTable;
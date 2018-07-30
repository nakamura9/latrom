import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {AsyncSelect, Heading, TableContent} from '../src/base_table';
import $ from 'jquery';

export default class OrderTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            contents: [],
            total: 0
        }
    }

    componentDidMount(){
        if(this.props.populated){
            var url = window.location.href;
            var url_elements = url.split("/");
            var pk = url_elements[url_elements.length - 1];

            $.ajax({
                url: '/inventory/api/order/' + pk + "/",
                method: 'GET'
            }).then(res => {
                console.log(res);
                var i=0;
                var newContents = this.state.contents
                var entries = res.orderitem_set;
                for(i in entries){
                    newContents.push({
                        'item_name': entries[i].item.code + 
                                        ' - ' + entries[i].item.item_name,
                        'description': entries[i].item.unit_price,
                        'quantity': entries[i].quantity,
                        'order_price': entries[i].order_price,                'unit': entries[i].item.unit
                    });
                }
                this.setState({contents: newContents})
            });
        }
    }
    
    insertHandler(vals){
        var newContents = this.state.contents;
        newContents.push(vals);
        var total = newContents.reduce((a, b) =>{
            return a + (b.quantity * b.order_price);
        }, 0);
        this.setState({
            contents: newContents,
            total: total
            });

        $('<input>').attr({
            type: 'hidden',
            name: 'items[]',
            id: "item_" + vals.item_name,//pk
            value: encodeURIComponent(JSON.stringify(vals))
        }).appendTo('form');
    }
    
    removeHandler(id){
        var newContents = this.state.contents;
        //id index of array
        console.log('called');
        if($('#item_' + id + 1).length){
            $('#item_' + id + 1).remove();
        }else{
            console.log('no item');
            if(this.props.populated){
                // identify existing elements and remove them.
                console.log('populated');
                $("<input>").attr({
                    "type": "hidden",
                    "name": "removed_items[]",
                    "id": "removed_item_" + id,
                    "value": this.state.contents[id].item_name
                    }).appendTo("form");
            }
        }
        var total = newContents.reduce((a, b) =>{
            return(a + (b.order_price * b.quantity));
        }, 0);
        
        this.setState({
            contents: newContents,
            total: total
            });

        newContents.splice(id, 1);
    }

    subtotalHandler(row){
        return(row.order_price * row.quantity);
    }
    
    render(){
        var entry_field_names = ['description', 'quantity', 'order_price', 'unit']
        var field_names = ['item_name'].concat(entry_field_names);
        return(
            <table>
                <Heading fields={this.props.fields}/>
                <TableContent contents={this.state.contents}
                    fields={field_names}
                    removeHandler={this.removeHandler.bind(this)}
                    subtotalHandler={this.subtotalHandler.bind(this)}/>
                <OrderTableEntry total={this.state.total} 
                    fields={entry_field_names}  
                    insertHandler={this.insertHandler.bind(this)} />
            </table>
        )
    }
}

class OrderTableEntry extends Component{
    constructor(props){
        super(props);
        this.state = {
            inputs: {}
        }
    }
    insertHandler(){
        this.props.insertHandler(this.state.inputs);
    }
    inputHandler(event){
        var name= event.target.name;
        var value = event.target.value;
        var newVals = this.state.inputs;
        newVals[name] = value;
        this.setState({inputs: newVals});
    }

    itemSelectHandler(event){
        this.inputHandler(event);
        let pk = event.target.value;
        
        $.ajax({
            method: "GET",
            url: "/inventory/api/item/" + pk + "/"
        }).then(res => {
            $("input[name='description']").val(res.description);
            $("input[name='order_price']").val(res.unit_purchase_price);
            $("input[name='unit']").val(res.unit);
            
            this.setState({
                inputs :{
                    item_name: res.code,
                    description: res.description,
                    order_price: res.unit_purchase_price,
                    unit: res.unit 
                }
            });
        })
    }

    render(){
        return(
            <tfoot>
                <tr>
                    <td></td>
                    <td>
                        <AsyncSelect url="/inventory/api/item/"
                            handleChange={this.itemSelectHandler.bind(this)} />
                    </td>
                    {this.props.fields.map((field, index) => (
                        <td key={index}><input type="text"
                               name={field} 
                               className="form-control"
                               onChange={event => (this.inputHandler(event))} />
                        </td>
                    ))}
                    
                </tr>
                <tr>
                    <td colSpan={this.props.fields.length + 1}></td>
                    <td>
                    <button type="button" 
                    className="btn btn-primary btn-lg"
                    onClick={this.insertHandler.bind(this)}>Insert</button>
                    </td>
                </tr>
                <tr>
                    <td colSpan='6'style={{textAlign: 'right'}}><b>Total:</b></td>
                    <td>{this.props.total}</td>
                </tr>
            </tfoot>
        );
    }
}




    
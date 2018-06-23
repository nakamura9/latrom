import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import {Heading, TableContent} from './src/base_table';
import $ from 'jquery';

class DirectPurchaseEntry extends Component {
    constructor(props){
        super(props);
        this.state = {
            inputs: {
                'name': '',
                'price': '',
                'description': ''
            },
        }
    }

    inputHandler(evt){
        let input = evt.target;
        let value = input.value;
        let newInputs = this.state.inputs;
        newInputs[input.name] = value;
        this.setState({inputs: newInputs});
    }

    addHandler(){
        this.props.addHandler(this.state.inputs);
        this.setState({
            inputs: {
                'name': '',
                'price': '',
                'description': ''
            }
        });
        $('input[name=name]').val("");
        $('input[name=price]').val("");
        $('input[name=description]').val("");
    }
    render(){
        return(
            <tfoot>
                <tr>
                    <td style={{
                        width: '10%',
                        backgroundColor: 'steelblue',
                        border: '1px solid white'    
                    }}></td>
                    <td style={{width: '15%'}}>
                        <input type="text" 
                            name="name" 
                            placeholder="Enter name here..." className="form-control"
                            onChange={this.inputHandler.bind(this)} />
                    </td>
                    <td style={{width: '60%'}}>
                        <input type="text" 
                            placeholder="Enter description here..." 
                            name="description" 
                            className="form-control"
                            onChange={this.inputHandler.bind(this)} />
                    </td>
                    <td style={{width: '15%'}}>
                        <input type="number" 
                            name="price" 
                            placeholder="Enter price here..." className="form-control"
                            onChange={this.inputHandler.bind(this)} />
                    </td>
                    
                </tr>
                <tr>
                    <td colSpan={3}></td>
                    <td>
                    <b>Total: {this.props.total}</b>
                    </td>
                </tr>
                <tr>
                    <td colSpan={3}></td>
                    <td>
                        <button className="btn btn-primary pull-right"
                            onClick={this.addHandler.bind(this)} >Add Item</button>
                    </td>
                </tr>

            </tfoot>
        );
    }
}


class PurchaseTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            contents: [],
            total: 0
        };
    }
    addHandler(data){
        
        let newContents = this.state.contents;
        newContents.push(data);
        let newTotal = newContents.reduce((a, b) =>{
            return( a + parseFloat(b.price) );
        }, 0);
        this.setState({
            contents: newContents,
            total: newTotal
        });
        
        $('<input>').attr({
                type: 'hidden',
                value: encodeURIComponent(JSON.stringify(data)),
                id: 'item_' + newContents.length
            }).appendTo('form');
 
        
    }

    removeHandler(index){
        let newContents = this.state.contents;
        newContents.splice(index, 1);
        let i = index + 1;
        let id = "#item_" + i;
        console.log(id)
        $(id).remove();
        this.setState({
            contents: newContents
        });
    }


    render(){
        var headings = ['Name', 'Description','Price'];
        var fields = ['name',  'description', 'price'];
        return(
            <table style={{width: '100%'}}>
                <Heading fields={headings} />
                <TableContent contents={this.state.contents}
                    removeHandler={this.removeHandler.bind(this)}
                    fields={fields}
                    subtotalHandler={(row) => ('')} />
                <DirectPurchaseEntry addHandler={this.addHandler.bind(this)}
                    total={this.state.total} />
            </table>
        );
    }
}

ReactDOM.render(<PurchaseTable />, document.getElementById('direct-purchase-table'));
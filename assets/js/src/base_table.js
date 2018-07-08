import React, {Component} from 'react';
import $ from 'jquery';

class Heading extends Component{
    //props of an array
    render(){
        var style = {
                backgroundColor: 'black',
                color: 'white',
                padding: '10px',
                borderLeft: '1px solid white'
            };
        return(
            <thead style={style}>
                <tr>
                <td style={{minWidth: '50px'}}></td>
                    {this.props.fields.map((field, index) =>(
                        <td style={style} key={index} > {field} </td>
                    ))}
                </tr>
            </thead>
        );
    }
}

class TableContent extends Component{
    render(){
        return(
            <tbody>
                {this.props.contents.map((row, index) =>(
                    <tr key={index}>
                        <td> 
                            <button type="button" 
                                    className="btn btn-danger"
                                    onClick={() => (this.props.removeHandler(index))}>
                                    <i className="fas fa-trash"></i>
                            </button>
                        </td>
                        {this.props.fields.map((field, i) =>(
                            <td key={i}>{row[field]}</td>
                        ))}
                        <td>
                            {this.props.subtotalHandler(row)}
                        </td>
                    </tr>
                ))}
            </tbody>
        ); 
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

class AsyncSelect extends Component{
    constructor(props){
        super(props);
        this.state = {
            options: []
        }

    }

    componentDidMount(){
        $.ajax({
            method: "GET",
            url: this.props.url,
            data: {}
        }).then(res => {
                var i;
                var newState = this.state.options;
                for(i in res){
                    newState.push({
                        pk: res[i].code,
                        name: res[i].item_name
                    });
                }
                this.setState({options: newState});
            }
        );
    }
    
    render(){
        return(
            <select name="item_name" onChange={event => this.props.handleChange(event)} className="form-control">
                <option value="">-------</option>
                {this.state.options.map((option, index) =>
                (
                    <option key={index} value={option.pk}>{option.pk} - {option.name}</option>
                ))}
            </select>
        );
    }
}

export { TableContent, OrderTableEntry, Heading};
import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

class TransferItems extends Component{
    constructor(props){
        super(props);
        this.state = {
            items: [],
            lines: [],
            inputs: {}
        }
    }

    componentDidMount(){
        document.getElementById('id_source_warehouse').addEventListener(
            'change', this.getItems.bind(this)
        )
    }

    getItems(evt){
        $.ajax({
            'url': '/inventory/api/warehouse-items/' + evt.target.value,
            'method': 'GET'
        }).then(res => {
            this.setState({items: res})
        });
        }

    addItem(){
        //create hidden input
        $('<input>').attr({
            type: 'hidden',
            value: encodeURIComponent(
                JSON.stringify(this.state.inputs)),
            name: 'items[]'
        }).appendTo('form');

        //create table row
        let newLines = this.state.lines;
        newLines.push(this.state.inputs);
        this.setState({lines: newLines});
    }

    removeHandler(){
        alert('removed');
    }

    handleInputChange(evt){
        let name = evt.target;
        let newInputs = this.state.inputs;
        newInputs[name] = evt.target.value;
        this.setState({newInputs: inputs});
    }

    render(){
        return(
            <table className="table">
    <thead>
        <tr className="bg-primary">
            <th>Item</th>
            <th>Quantity</th>
            <th></th>
        </tr>
        <tr>
            
            <td>
                <input type="text" 
                    className="form-control"
                    list="item-list"
                    name="item"
                    onChange={this.handleInputChange.bind(this)}
                    />
                <datalist id='item-list'>
                    {this.state.items.map((item, i) =>(
                        <option value={item.id + "-" + item.item.item_name} />
                    ))}
                </datalist>
            </td>
            <td>
                <input type="number" 
                    className="form-control"
                    name="quantity"
                    onChange={this.handleInputChange.bind(this)}/>
            </td>
            <td>
                    <button className="btn btn-primary"
                        onClick={this.addItem.bind(this)}>Add Item</button>
            </td>
        </tr>
    </thead>
    <tbody>
            {this.state.lines.map((line, i) =>(
                <TransferLine data={line}
                    removeHandler={this.removeHandler.bind(this)}/>
            )) }
    </tbody>
</table>
        );
    }
}

class TransferLine extends Component{
    render(){
        return(
            <tr>
                <td>
                    <button className="btn btn-danger"
                        onClick={this.props.removeHandler}>
                        <i className="fas fa-trash" ></i>
                    </button>
                </td>
                <td>{this.props.data.name}</td>
                <td>{this.props.data.quantity}</td>
        </tr>
        );
    }
}

ReactDOM.render(<TransferItems />, document.getElementById('transfer-items'))
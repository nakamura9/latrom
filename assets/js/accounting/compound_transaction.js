import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import setMultipleAttrs from '../src/utils';
import SearchableWidget from '../src/components/searchable_widget';
import axios from "axios";

export default class TransactionTable extends Component{
    state = {
            contents: [],
            balanced: 0,
        }

  
    
    balance =() =>{
        let i = 0;
        const transactions = this.state.contents;
        var debit =0;
        var credit = 0;
        for(i=0; i < transactions.length; i++){
            if(transactions[i].debit === "0"){
                credit = credit + parseFloat(transactions[i].amount);
            }else{
                debit = debit + parseFloat(transactions[i].amount);
            }
        }
        if(credit === debit){
            this.setState({balanced: 1});
        }else{
            this.setState({balanced: 0});
        }
        
    }
    addHandler =(data) =>{
        let form = document.forms[0];
        //jquery replacement
        let newContents = this.state.contents;
        newContents.push(data);

        let input = document.createElement("input");
        setMultipleAttrs(input, {
            type: 'hidden',
            id: 'item_' + this.state.contents.length,
            name: 'items[]',
            value: encodeURIComponent(JSON.stringify(data))
        })
        form.appendChild(input);

        this.setState({contents: newContents}, this.balance);
    }

    removeHandler =(index) =>{
        let newContents = this.state.contents;
        newContents.splice(index, 1);
        document.getElementById("item_" + (index + 1)).remove();

        this.setState({contents: newContents}, this.balance);
        
    }
    
    render(){
        return(
            <table className="table table-striped" >
            <thead>
                <tr className="bg-primary text-white" >
                    <th></th>
                    <th>Account</th>
                    <th>Amount</th>
                    <th>Credit/Debit</th>
                </tr>
            </thead>
            <Content contents={this.state.contents}
                removeHandler={this.removeHandler} />
            <EntryRow 
                addHandler={this.addHandler}
                balanced={this.state.balanced}
                list={[...this.state.contents]} />
        </table>
        );
        
    }
}

class Content extends Component{
    render(){
        return(
            <tbody>
            {this.props.contents.map((item, index) => (
                <tr key={index}>
                    <td>
                        <button className="btn btn-danger" type="button"
                            onClick={() =>this.props.removeHandler(index)} >
                            <i className="fas fa-trash"></i>
                        </button>
                    </td>
                    <td>{item.account}</td>
                    <td>{item.amount}</td>
                    <td>{item.debit === "1" ? 'Debit' : 'Credit'}</td>
                </tr>
            ))}
        </tbody>
        );
        
    }
}
class EntryRow extends Component {
    state = {
            inputs: {
                'account': '',
                'amount': 0,
                'debit': ""
            }
        }
    
    addHandler = () =>{
        if(this.state.inputs.account === "" || 
                this.state.inputs.amount === 0 ||
                    this.state.inputs.debit === ""){
            alert('Please provide the necessary data!');
        }else{
            this.props.addHandler(this.state.inputs);
            this.setState({inputs: {
                'account': '',
                'amount': 0,
                'debit': ""
            }})
        }
        
    }

    handleInputChange = (evt) =>{
        let name = evt.target.name;
        let value = evt.target.value;
        let newInputs = this.state.inputs;
        newInputs[name] = value;
        this.setState({inputs: newInputs});

    }
    
    selectHandler = (value) =>{
        let inputs = {...this.state.inputs};
        inputs["account"] = value;
        this.setState({inputs: inputs});
    }

    clearHandler = () =>{
        let inputs = {...this.state.inputs};
        inputs["account"] = "";
        this.setState({inputs: inputs});
    }

    render(){
        return(
            <tfoot>
                <tr>
                    <td colSpan={2}>
                        <SearchableWidget
                            list={this.props.list}
                            dataURL="/accounting/api/account"
                            displayField="name"
                            idField="id"
                            onSelect={this.selectHandler}
                            onClear={this.clearHandler}/>
                    </td>
                    <td>
                        <input name="amount" 
                            type="number" 
                            value={this.state.inputs.amount}
                            className="form-control"
                            onChange={this.handleInputChange} />
                    </td>
                    <td>
                        <select name="debit" 
                            value={this.state.inputs.debit}
                            className="form-control"
                            onChange={this.handleInputChange}>
                            <option value="">-----</option>
                            <option value={1}>Debit</option>
                            <option value={0}>Credit</option>
                        </select>
                    </td>
                </tr>
                <tr className={this.props.balanced === 1?
                        "bg-success" :
                        "bg-danger"} >
                   <td colSpan={3} style={{
                       fontSize: "24",
                       textAlign: 'center',
                       color: 'white'
                   }} >{this.props.balanced === 1 ? 
                                        "Balanced" : 
                                        "Unbalanced"}</td>
                   <td>
                        <button className="btn btn-primary" type="button" 
                            onClick={this.addHandler}>
                        Insert Transaction
                        </button>
                   </td>
                </tr>
            </tfoot>
        );
    }
}


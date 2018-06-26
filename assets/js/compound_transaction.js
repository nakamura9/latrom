import React, {Component} from 'react';
import ReactDOM from 'react-dom';

class TransactionTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            contents: [],
            balanced: 0,
        }
    }
    balance(){
        let i = 0;
        const transactions = this.state.contents;
        var debit =0;
        var credit = 0;
        for(i in transactions){
            if(transactions[i].debit === "0"){
                credit = credit + parseFloat(transactions[i].amount);
            }else{
                debit = debit + parseFloat(transactions[i].amount);
            }
        }
        console.log('credit: ' + credit);
        console.log('debit: ' + debit);
        if(credit === debit){
            this.setState({balanced: 1});
        }else{
            this.setState({balanced: 0});
        }
        
    }
    addHandler(data){
        let newContents = this.state.contents;
        newContents.push(data);
        
        this.balance();
        $("<input>").attr({
            type: 'hidden',
            id: 'item_' + this.state.contents.length,
            name: 'items[]',
            value: encodeURIComponent(JSON.stringify(data))
        }).appendTo('form');
        this.setState({contents: newContents});
    }

    removeHandler(index){
        let newContents = this.state.contents;
        newContents.splice(index, 1);
        this.setState({contents: newContents});
        this.balance();
        $("#item_" + index).remove();
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
                removeHandler={this.removeHandler.bind(this)} />
            <EntryRow addHandler={this.addHandler.bind(this)}
                balanced={this.state.balanced} />
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
                        <button className="btn btn-danger"
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
    constructor(props){
        super(props);
        this.state = {
            accounts: [],
            inputs: {
                'account': '',
                'amount': 0,
                'debit': ""
            }
        }
    }

    componentDidMount(){
        $.ajax({
            'url': '/accounting/api/account/', 
            'method': 'get'
        }).then((res) => {
            this.setState({'accounts': res});
        });
    }

    addHandler(){
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
            $('select[name=account]').prop('selectedIndex', 0);
            $('select[name=debit]').prop('selectedIndex', 0);
            $('input[name=amount]').val("");
        
        }
        
    }

    handleInputChange(evt){
        let name = evt.target.name;
        let value = evt.target.value;
        let newInputs = this.state.inputs;
        newInputs[name] = value;
        this.setState({inputs: newInputs});

    }

    render(){
        return(
            <tfoot>
                <tr>
                    <td colSpan={2}>
                        <select name="account" 
                            className="form-control"
                            onChange={this.handleInputChange.bind(this)} >
                            <option value="">-----</option>
                            {this.state.accounts.map((acc, index) =>(
                                <option key={index} value={acc.id}> {acc.name}</option>
                            ))}
                        </select>
                    </td>
                    <td>
                        <input name="amount" 
                            type="number" 
                            className="form-control"
                            onChange={this.handleInputChange.bind(this)} />
                    </td>
                    <td>
                        <select name="debit" 
                            className="form-control"
                            onChange={this.handleInputChange.bind(this)}>
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
                        <button className="btn btn-primary" 
                            onClick={this.addHandler.bind(this)}>
                        Insert Transaction
                        </button>
                   </td>
                </tr>
            </tfoot>
        );
    }
}

ReactDOM.render(<TransactionTable />, document.getElementById('transaction-table'))
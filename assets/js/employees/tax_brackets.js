import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class TaxBracketTable extends Component{
    constructor(props){
        super(props);
        this.state = {
            brackets : []
        }
    }

    componentDidMount(){
        $('<input>').attr({
            'name': 'brackets',
            'id': 'id_brackets',
            'type': 'hidden',
        }).appendTo('form');
    }

    insertHandler(data){
        let newBrackets = this.state.brackets;
        newBrackets.push(data);
        this.setState({brackets: newBrackets});
        this.updateForm();
    }

    removeHandler(index){
        let newBrackets = this.state.brackets;
        newBrackets.splice(index, 1);
        this.setState({brackets: newBrackets});
        this.updateForm();
    }

    updateForm(){
        $('#id_brackets').val(
           encodeURIComponent(
               JSON.stringify(this.state.brackets))
        );
    }

    render(){
        return(
            <table>
    <thead>
        <tr>
            <th></th>
            <th>Lower Limit</th>
            <th>Upper Limit</th>
            <th>Rate(%)</th>
            <th>Deduction</th>
        </tr>
    </thead>
    <tbody>
        {this.state.brackets.map((bracket, index) => (
            <tr key={index}>
                <td>
                    <button onClick={() => (this.removeHandler(index))}>
                        <i className='fas fa-trash'></i>
                    </button>
                </td>
                <td>{bracket.lower_limit}</td>
                <td>{bracket.upper_limit}</td>
                <td>{bracket.rate}</td>
                <td>{bracket.deduction}</td>
            </tr>
        ))}
    </tbody>
    <PayrollTaxEntryRow insertHandler={this.insertHandler.bind(this)}/>
</table>
        );
    }
}

class PayrollTaxEntryRow extends Component{
    constructor(props){
        super(props);
        this.state = {

        }
    }

    insertHandler(){
        let lower_limit = $('input[name=lower_limit]');
        let upper_limit = $('input[name=upper_limit]');
        let rate = $('input[name=rate]');
        let deduction = $('input[name=deduction]');
        
        if(lower_limit.val() === "" || upper_limit.val() === "" ||
            rate.val() === "" || deduction.val() == ""){
                alert('Please enter all the required fields');
            }else{
                this.props.insertHandler(this.state);
        lower_limit.val("");
        upper_limit.val("");
        rate.val("");
        deduction.val("");
            }
        
    }

    inputChangeHandler(evt){
        let newState = this.state
        let input_name =evt.target.name;
        newState[input_name] = evt.target.value;
        this.setState(newState);
    }
    
    render(){
        return(
            <tfoot>
        <tr>
            <td></td>
            <td><input type="number" 
                name="lower_limit"
                onChange={this.inputChangeHandler.bind(this)}/></td>
            <td><input type="number" 
                name="upper_limit"
                onChange={this.inputChangeHandler.bind(this)} /></td>
            <td><input type="number" 
                name="rate"
                onChange={this.inputChangeHandler.bind(this)}/></td>
            <td><input type="number" 
                name="deduction"
                onChange={this.inputChangeHandler.bind(this)} /></td>
        </tr>
        <tr>
            <td colSpan={5}>
                <button onClick={this.insertHandler.bind(this)}>Insert Row</button>
            </td>
        </tr>
    </tfoot>
        );
    }
}


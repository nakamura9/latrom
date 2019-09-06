import React, {Component} from 'react';
import {AsyncSelect} from '../../../src/common';
import axios from 'axios';

class Calculator extends Component{
    state = {
        calculated_value: 0,
        input: 0,
        options: [],
        selected: null
    }

    tableDataProcessor = (res) =>{
        return res.data.map((item, i) => ({
            name: item.name,
            value: item.id
        }));
    }

    componentDidUpdate(prevProps, PrevState){
        if(this.props.table && this.props.table != prevProps.table){
            axios({
                method: 'GET',
                url: '/accounting/api/currency-conversion-table/' + this.props.table
            }).then(res =>{
                this.setState({options: res.data.currencyconversionline_set})
            })
        }
        
    }

    inputHandler = (evt) =>{
        this.setState({input: evt.target.value}, this.calculateResult);
        
    }

    currencyHandler = (evt) =>{
        this.setState({
            selected: this.state.options[evt.target.value]
        })
    }

    calculateResult = () =>{
        if(this.state.selected){
            this.setState({
                calculated_value: this.state.input * 
                    this.state.selected.exchange_rate
            })
        }

    }
    render(){
        return(
            <div>
                <h4>Calculator</h4>
                <table className="table table-sm">
                    <tbody>
                        <tr>
                            <th>Currency</th>
                            <td>
                                <select 
                                    className="form-control"
                                    onChange={this.currencyHandler}>
                                    <option value>-----</option>
                                    {this.state.options.map((opt, i) =>(
                                        <option value={i}>{opt.currency.name}</option>))}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <th>Amount</th>
                            <td>
                                <input 
                                    type="number"
                                    className="form-control"
                                    value={this.state.input}
                                    onChange={this.inputHandler}/>
                            </td>
                        </tr>
                        <tr>
                            <th>Calculated:</th>
                            <td>{this.state.calculated_value}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    }
}

export default Calculator;
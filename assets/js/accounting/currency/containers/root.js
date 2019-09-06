import React, {Component} from 'react';
import Calculator from '../components/calculator';
import CurrencyList from '../components/currency_list';
import ExchangeTable from '../components/exchange_table';
import axios from 'axios';
import $ from 'jquery';

class CurrencyConverter extends Component{
    state = {
        exchangeTable: null,
        tableOptions: [],
        formData: {
            name: '',
            reference_currency_id: null
        },
        createExchangeTableMode: false,
        currencies: [],
        token: ""
    }


    inputHandler = (evt) =>{
        const val = evt.target.value;
        const name = evt.target.name;
        let newFormData = this.state.formData;
        newFormData[name] = val;
        this.setState({formData: newFormData});
    }
    
    updateCurrencyList = () =>{
        axios({
            method: 'GET',
            url: '/accounting/api/currency/'
        }).then( res =>{
            this.setState({currencies: res.data})
        })
    }

    setExchangeTable = (evt) =>{
        this.setState({exchangeTable: evt.target.value});

    }


    toggleCreateExchangeTableMode = () =>{
        this.updateCurrencyList();
        this.setState((prevState) =>({
            createExchangeTableMode: !prevState.createExchangeTableMode}));
    }

    setTables = () =>{
        //populate table options 
        axios({
            method: 'GET',
            url: '/accounting/api/currency-conversion-table/'
        }).then(res =>{
            this.setState({tableOptions: res.data});
        });

        axios({
            method: 'GET',
            url: '/accounting/api/settings/1'
        }).then(res =>{
            this.setState({exchangeTable: res.data.currency_exchange_table});
        });
    }

    componentWillMount(){
        if(this.state.token ===""){
            this.setState({token: $("input[name='csrfmiddlewaretoken']").val()})
        }
    }
    componentDidMount(){
        this.setTables();
        this.updateCurrencyList();
    }

    render(){
        return(
            <div className='row'>
                <div  
                className="col-6 card shadow">
                    <div className='card-body'>
                        <Calculator 
                        currencies={this.state.currencies}
                        table={this.state.exchangeTable}/>
                    <CurrencyList 
                        currencies={this.state.currencies}
                        currencyRefresher={this.updateCurrencyList}/>
                    </div>
                </div>
                <div className='col-6'>
                    <div className='form-group row' style={{paddingLeft: "10px"}}><label htmlFor="exchange-table">Exchange Table</label>
                        <select
                            name='exchange-table'
                            className="form-control"
                            style={{
                                    display: 'inline-block',
                                    width: '250px'
                                }}
                            onChange={this.setExchangeTable}
                            value={this.state.exchangeTable}>
                            <option value={0}>-------</option>
                            {this.state.tableOptions.map((opt, i) =>(
                                <option 
                                    key={i}
                                    value={opt.id}>{opt.name}</option>
                            ))}
                        </select> <button 
                        style={{
                            display: this.state.createExchangeTableMode 
                                ? 'none'
                                : 'block'
                        }}
                        className="btn btn-primary"
                        onClick={this.toggleCreateExchangeTableMode}>
                            <i className="fas fa-plus"></i>        
                    </button></div>
                    <br />
                    <div style = {{
                        display: this.state.createExchangeTableMode
                            ?   'block'
                            : 'none'
                    }}>
                        <h5>Exchange Table Creation Form</h5>
                        <form method="POST" action="/accounting/create-exchange-table/">
                            <input 
                                type="hidden"
                                value={this.state.token}
                                name="csrfmiddlewaretoken"/>
                            <input
                                className="form-control"
                                placeholder="enter table name"
                                value={this.state.formData.name}
                                onChange={this.inputHandler} 
                                name="name"
                                />
                            <select 
                                className="form-control"
                                name="reference_currency"
                                onChange={this.inputHandler}>
                                <option value>Select Currency</option>
                                {this.state.currencies.map((opt, i) =>(
                                    <option 
                                        key={i}
                                        value={opt.id}>{opt.name}</option>))}
                            </select>
                                <button 
                                    type="submit"
                                    className="btn btn-primary"
                                    >Save New Table</button>
                        </form>
                    </div>
                    
                    
                    <hr />
                   <ExchangeTable 
                        tableID={this.state.exchangeTable}
                        currencies={this.state.currencies}/> 
                </div>
            </div>
        )
    }
}

export default CurrencyConverter;
import React, {Component} from 'react';
import { AsyncSelect } from '../../../src/common';
import axios from 'axios';

export default class ExchangeTable extends Component{
    state = {
        reference_currency: {},
        currencies: [],
        editing: false,
        rates: [],
        name: "",
        createRateMode: false,
        newRateData: {
            currency_id: null,
            rate: 0
        }
    }

    updateReferenceCurrency = (evt) =>{
        this.setState({
            reference_currency: this.state.currencies[evt.target.value]
        });
    }

    setTable = () =>{
        //use api to get table data
        if(this.props.tableID === 0){
            return;
        }else{
            axios({
                method: 'GET',
                url: `/accounting/api/currency-conversion-table/${this.props.tableID}/`
            }).then(res =>{
                this.setState({
                    reference_currency: res.data.reference_currency,
                    name: res.data.name,
                    rates: res.data.currencyconversionline_set.map((line, i)=>{
                        return(
                            {
                                editing: false,
                                exchange_rate: line.exchange_rate,
                                name: line.currency.name,
                                id: line.id
                            }
                        )
                    })
                })
            });
        }
    }


    componentDidMount(){
        // set up table
        this.setTable();
        
    }

    componentDidUpdate = (prevProps, prevState) => {
      if(prevProps.tableID !== this.props.tableID){
          this.setTable();
      }if(prevProps.currencies !== this.props.currencies){
          this.setState({currencies: this.props.currencies})
      }
    }
    
    updateRate = (evt, i) =>{
        let newRates = [...this.state.rates];
        let item = newRates[i];
        item.exchange_rate = evt.target.value;
        newRates[i] = item;
        this.setState({rates: newRates});
        //update rate on server
    }

    toggleRateEditing = (i) =>{
        let newRates = [...this.state.rates];
        let item = newRates[i];
        if(item.editing){
            $.ajax({
                method: 'POST',
                url: `/accounting/api/update-exchange-rate/${item.id}/`,
                data: {
                    rate: item.exchange_rate,
                    csrfmiddlewaretoken: 
                        $("input[name='csrfmiddlewaretoken']").val()
                }
            }).fail(() =>{alert('failed to update the server')})
        }
         
        item.editing = !item.editing;
        newRates[i] = item;
        this.setState({rates: newRates});
    }

    toggleReferenceEditing = () =>{
        if(this.state.editing){
            this.updateReferenceCurrencyOnServer();
        }
        this.setState((prevState) =>{
            return({editing: !prevState.editing});
        });
    }

    toggleCreateRateMode = () =>{
        if(this.state.createRateMode){
            //form with currency, exchange rate and exchang_table
            $.ajax({
                method: 'POST',
                url: '/accounting/api/create-conversion-line/',
                data: {
                    ...this.state.newRateData,
                    table_id: this.props.tableID,
                    csrfmiddlewaretoken: 
                        $("input[name='csrfmiddlewaretoken']").val()
                }
            })
            .then(this.setTable)
            .fail(() =>{alert('failed to communicate with server')});
        }
        this.setState((prevState) =>{
            return({createRateMode: !prevState.createRateMode})
        });
    }

    updateReferenceCurrencyOnServer = () =>{
        axios.get(
            `/accounting/api/update-reference-currency/${this.props.tableID}/${this.state.reference_currency.id}`)
    }

    newRateInputHandler =(evt) =>{
        let updatedRateData = {...this.state.newRateData};
        const name = evt.target.name;
        const value = evt.target.value;
        updatedRateData[name] = value;

        this.setState({newRateData: updatedRateData});
    }
    render(){

        const invalidID = <h3>Select a valid currency table</h3>;
        const validID = (
            <div >
                <p><b>Reference Currency: </b> {
                    this.state.editing
                    ? <select 
                            className="form-control"
                            style={{
                                display: "inline-block",
                                width: "200px"
                            }}
                            onChange={this.updateReferenceCurrency}>
                        <option value selected>Select new reference</option>
                        {this.state.currencies.map((cur, i) =>(
                            <option 
                                value={i}
                                key={i}>{cur.name}</option>
                        ))}
                    </select>
                    : this.state.reference_currency.name
                }
                    <button
                        className="btn btn-primary btn-sm"
                        onClick={() =>this.toggleReferenceEditing()}>
                        <i 
                            className={`fas fa-${this.state.editing ? 'check' : 'edit'}`}></i>
                    </button>
                </p>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th style={{width:"60%"}}>Currency</th>
                            <th>Rate</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.rates.map((rate, i) =>(
                            <tr key={i}>
                                <td>{rate.name}</td>
                                <td>
                                    {
                                        rate.editing
                                        ? <input 
                                        type="number"
                                        style={{
                                            width: "200px",
                                            display: 'inline-block'
                                        }}
                                        className="form-control"
                                        placeholder={rate.exchange_rate}
                                        onChange={
                                            (evt) => this.updateRate(evt, i)}/>
                                        : rate.exchange_rate
                                    }
                                </td>
                                <td>
                                    <button 
                                        onClick={() => this.toggleRateEditing(i)}
                                        className="btn btn-success btn-sm">
                                        <i className={`fas fa-${rate.editing ? 'check' : 'edit' }`}></i>    
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot style={{
                        display: this.state.createRateMode 
                                    ? 'block'
                                    : 'none'
                                }}>
                                
                        <tr>
                                <td>
                                    <select
                                        name="currency_id"
                                        className="form-control"
                                        onChange={this.newRateInputHandler}>
                                        <option value>Select Currency</option>
                                        {this.state.currencies.map((cur, i) =>(
                                            <option 
                                                value={cur.id}
                                                key={i}>{cur.name}</option>
                                        ))}
                                    </select>
                                </td>
                                <td colSpan={2}>
                                    <input 
                                        name="rate"
                                        type="number"
                                        placeholder="enter rate..."
                                        className="form-control"
                                        onChange={this.newRateInputHandler}/>
                                </td>
                        </tr>
                    </tfoot>    
                </table>

                <button 
                    className="btn btn-primary btn-sm"
                    onClick={this.toggleCreateRateMode}
                    >
                    {this.state.createRateMode
                        ? 'Save' : 'Add' } Exchange Rate</button>
            </div>
        );

        //actual rendering here
        if(this.props.tableID){
            return(validID);
        }else{
            return(invalidID);
        }
        
    }
}
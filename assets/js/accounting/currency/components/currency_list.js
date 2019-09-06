import React, {Component} from 'react';
import axios from 'axios';
import $ from 'jquery';


export default class CurrencyList extends Component{
    state = {
        currencies: [],
        currencyCreateMode: false,
        newCurrencySymbol: "",
        newCurrencyName: ""
    }

    componentDidUpdate = (prevProps, prevState) => {
      if (prevProps.currencies !== this.props.currencies){
          this.setState({currencies: this.props.currencies})
      }
    }
    


    inputHandler = (evt) =>{
        const type = evt.target.name;
        if(type === "name"){
            this.setState({newCurrencyName: evt.target.value});
        }else{
            this.setState({newCurrencySymbol: evt.target.value});
        }
    }

    toggleCurrencyCreateMode = () =>{
        if(this.state.currencyCreateMode){
            if(this.state.newCurrencyName !== "" && 
                this.state.newCurrencySymbol !== ""){
                    const token = $("input[name='csrfmiddlewaretoken']").val();
                    $.ajax({
                        method: 'POST',
                        url: '/accounting/api/currency/',
                        data: {
                            name: this.state.newCurrencyName,
                            symbol: this.state.newCurrencySymbol,
                            csrfmiddlewaretoken: token
                        }
                    }).then(this.props.currencyRefresher)
                }
        }
        this.setState((prevState) =>{
            return({currencyCreateMode: !prevState.currencyCreateMode})
        })
    }
    render(){
        return(
            <div>
            <h4>Currency List</h4>
            <div style={{
                maxHeight: "300px",
                overflowY: "auto"
            }}>
                <table className="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Symbol</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.currencies.map((c, i) =>(
                            <tr key={i}>
                                <td>{c.name}</td>
                                <td>{c.symbol}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className='form-group form-row' style={{
                display: this.state.currencyCreateMode ? "block" : "none"
            }}>
               <div className="col-6">
                <input
                    type="text"
                    className="form-control"
                    value={this.state.newCurrencyName}
                    name="name"
                    onChange={this.inputHandler}
                    placeholder="Enter Currency Name" />
               </div>
               <div className="col-6">
                    <input
                        type="text"
                        className="form-control"
                        value={this.state.newCurrencySymbol}
                        name="symbol"
                        onChange={this.inputHandler}
                        placeholder="Enter Currency Symbol" />
               </div>
            </div>
            <button 
                className="btn btn-secondary btn-sm"

                onClick={this.toggleCurrencyCreateMode}>
                {this.state.currencyCreateMode 
                    ? 'Save' 
                    : 'Register'} New Currency
                </button>
        </div>
        )
        
    }
}
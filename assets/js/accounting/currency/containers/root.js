import React, {Component} from 'react';
import Calculator from '../components/calculator';
import CurrencyList from '../components/currency_list';
import ExchangeTable from '../components/exchange_table';

class CurrencyConverter extends Component{
    state = {
        rates: [{
            'exchange_rate': 1,
            'reference_currency': 'BOND',
            'exchange_currency': 'USD'
        }],
        currencies: [
            {
                'name': 'bond',
                'symbol': '$'
            }
        ],
        calculated_value: 0,
        input: 0
    }

    inputHandler = (evt) =>{
        this.setState({
            input: evt.target.value,
            calculated_value: evt.target.value
        });
        //calculate the value and set state
    }
    render(){
        return(
            <div>
                <div  style={{
                    backgroundColor: "#0cc",
                    width: "30%",
                    display: "inline-block",
                    padding: "30px"
                }}>
                    <Calculator />
                    <CurrencyList />
                </div>
                <div style={{
                    width: "60%",
                    display: "inline-block",
                    paddingLeft: "10px"
                }}>
                   <ExchangeTable /> 
                </div>
            </div>
        )
    }
}

export default CurrencyConverter;
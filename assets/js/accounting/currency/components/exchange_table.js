import React, {Component} from 'react';

export default class ExchangeTable extends Component{
    state = {
        rates: [{
            'exchange_rate': 1,
            'reference_currency': 'BOND',
            'exchange_currency': 'USD'
        }],
    }
    render(){
        return(
            <div >
                <h3>Exchange Table</h3>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>Reference Currency</th>
                            <th>Exchange Currency</th>
                            <th>Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {this.state.rates.map((rate, i) =>(
                            <tr key={i}>
                                <td>{rate.reference_currency}</td>
                                <td>{rate.exchange_currency}</td>
                                <td>
                                    {rate.exchange_rate}
                                    <button 
                                        className="btn btn-success">
                                        <i className="fas fa-edit"></i>    
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>    
                </table>
                <button className="btn btn-primary">
                    Add Exchange Rate</button>
            </div>
        )
    }
}
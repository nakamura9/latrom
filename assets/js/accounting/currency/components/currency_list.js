import React, {Component} from 'react';

export default class CurrencyList extends Component{
    state = {
        currencies: [
            {
                'name': 'bond',
                'symbol': '$'
            }
        ],
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
                            <td>Name</td>
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
            <button 
                className="btn btn-primary">
                Register New Currency
                </button>
        </div>
        )
        
    }
}
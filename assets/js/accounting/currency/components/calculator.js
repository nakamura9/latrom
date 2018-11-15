import React, {Component} from 'react';

class Calculator extends Component{
    state = {
        calculated_value: 0,
        input: 0
    }
    render(){
        return(
            <div>
                <h4>Calculator</h4>
                <table className="table">
                    <tbody>
                        <tr>
                            <td>Reference</td>
                            <td>Target</td>
                        </tr>
                        <tr>
                            <td>
                                <select className="form-control">
                                    <option>-----</option>
                                    <option>BOND</option>    
                                    <option>USD</option>
                                </select>
                            </td>
                            <td>
                                <select className="form-control">
                                    <option>-----</option>
                                    <option>BOND</option>    
                                    <option>USD</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <input 
                                    type="number"
                                    className="form-control"
                                    value={this.state.input}
                                    onChange={this.inputHandler}/></td>
                            <td style={{
                                color: "white",
                                fontWeight: "bold",
                                backgroundColor: "#07f"
                            }}>
                                {this.state.calculated_value}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    }
}

export default Calculator;
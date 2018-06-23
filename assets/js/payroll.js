import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import PayrollTable from './src/payroll_table';

class Payroll extends Component{
    render(){
        return(
            <div>
                <h3>Common Features</h3>
                <hr />
                <table>
                    <tbody>
                        <tr>
                            <th>Start Period</th>
                            <td>
                                <input className="form-control date" 
                                    type="text" 
                                    id="id_start_date"
                                    name="start-date" />
                            </td>
                        </tr>
                        <tr>
                            <th>End Period</th>
                            <td>
                                <input className="form-control date" 
                                    type="text"
                                    id="id_end_date" 
                                    name="end-date" />
                                </td>
                        </tr>
                    </tbody>
                </table>
                <hr />
                <h3>Payroll Table</h3>
                <hr />
                <PayrollTable  />
                </div>
            
        )
    }
}

ReactDOM.render(<Payroll />, 
    document.getElementById('payroll-table'));
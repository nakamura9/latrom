import React, {Component} from 'react';
import ShiftLine from '../components/shift_line';
import ShiftEntryLine from '../components/shift_entry';

class ShiftSchedule extends Component{
    state = {
        lines: []
    }
    
    render(){
        return(
            <table className="table">
                <thead>
                    <tr className="bg-primary text-white">
                        <th>Shift</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Mon</th>
                        <th>Tue</th>
                        <th>Wed</th>
                        <th>Thr</th>
                        <th>Fri</th>
                        <th>Sat</th>
                        <th>Sun</th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.lines.map((line, i) =>{
                        <ShiftLine data={line} key={i} />
                    })}
                </tbody>
                <ShiftEntryLine />
            </table>
        )
    }
}

export default ShiftSchedule;
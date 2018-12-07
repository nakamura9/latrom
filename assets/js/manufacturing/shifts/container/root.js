import React, {Component} from 'react';
import ShiftLine from '../components/shift_line';
import ShiftEntryLine from '../components/shift_entry';

class ShiftSchedule extends Component{
    state = {
        lines: []
    }

    insertHandler = (data) =>{
        let newLines = [...this.state.lines];
        newLines.push(data);
        this.setState({lines: newLines}, this.updateForm);
    }
    deleteHandler = (index) => {
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, this.updateForm)

    }

    updateForm = () =>{
        document.getElementById('id_shift_lines').value = encodeURIComponent(
            JSON.stringify(
                this.state.lines));
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
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {this.state.lines.map((line, i) =>(
                        <ShiftLine 
                            data={line} 
                            key={i}
                            index={i}
                            deleteHandler={this.deleteHandler} />
                    )
                    )}
                </tbody>
                <ShiftEntryLine 
                    insertHandler={this.insertHandler}/>
            </table>
        )
    }
}

export default ShiftSchedule;
import React, {Component} from 'react';
import $ from 'jquery';
import axios from 'axios';

export default class TimeSheet extends Component{
    state = {
        lines: []
    }

    componentDidMount(){
        $('<input>').attr({
            type: 'hidden',
            name: 'lines',
            id: "id_lines" ,
            value: ""
        }).appendTo('form');
        
        const urlSegments = window.location.href.split('/');
        const tail = urlSegments[urlSegments.length - 1];
        if(tail !== 'create'){
            axios({
                url: '/employees/api/timesheet/' + tail,
                method: 'GET',

            }).then(res =>{
                console.log(res.data)
                this.setState({lines: res.data.attendanceline_set.map((line) =>(
                    {
                        date: line.date,
                        timeIn: line.time_in,
                        timeOut: line.time_out,
                        breaksTaken: line.lunch_duration,
                    }
                ))})
            })
            $('#id_lines').val(encodeURIComponent(JSON.stringify(this.state.lines)));
        }
    }
    
    lineHandler = (data) =>{
        let newLines = [...this.state.lines];
        newLines.push(data);
        this.setState({lines: newLines}, () =>{
            $('#id_lines').val(encodeURIComponent(JSON.stringify(this.state.lines)));
        });
    }
    
    render(){
        let body = null;
        if(this.state.lines.length === 0){
            body = <tbody>
                    <TimeSheetFields 
                        insertLine={this.lineHandler}/>
                </tbody>
        }else{
            body = <tbody>
                    {this.state.lines.map((line, i) =>(
                        <TimeSheetLine 
                            key={i}
                            data={line}
                        />
                    ))}
                    <TimeSheetFields 
                        insertLine={this.lineHandler}/>
            </tbody>
        }
        return(
            <table className="table">
                <thead>
                    <tr className="bg-primary">
                        <th>Date</th>
                        <th>Time In</th>
                        <th>Time Out</th>
                        <th>Breaks Taken</th>
                        <th>Total Working Hours</th>    
                    </tr>    
                </thead>
                {body}
            </table>
        );
    }
}

const DayField = (props) => {
    const options = [...Array(31).keys()];
    return(<select 
                className="form-control"
                name={props.name} 
                onChange={props.handler}>
            <option value selected>-----</option>
            {options.map((opt, i) =>(
                <option value={i + 1 } key={i}>{i + 1}</option>
            ))}
        </select>)
}

const TimeField = (props) => {
    const hourOptions = ['00','01', '02', '03','04','05','06','07',
        '08','09','10','11','12','13','14','15','16','17','18','19',
        '20','21','22','23'];
    const minuteOptions = ['00', '15', '30', '45'];
    return(
        <select 
            className="form-control"
            name={props.name} 
            onChange={props.handler}>
            <option value selected>-----</option>
            {hourOptions.map((hour, i) =>(
                minuteOptions.map((minute, j) =>(
                    <option value={hour + ":" + minute}>{hour + ":" + minute}</option>
                ))
            ))}
        </select>
    )
}

class TimeSheetFields extends Component{
    state = {
        date: 0,
        timeIn: 0,
        timeOut: 0,
        breaksTaken: 0
    }
    inputHandler = (evt) =>{
        const name = evt.target.name;
        let newState = {...this.state};
        newState[name] = evt.target.value;
        this.setState(newState);
    }
    render(){
        return(<tr>
            <td><DayField 
                    name="date"
                    handler={this.inputHandler} /></td>
            <td><TimeField name="timeIn" handler={this.inputHandler}/></td>
            <td><TimeField name="timeOut" handler={this.inputHandler}/></td>
            <td><TimeField name="breaksTaken" handler={this.inputHandler}/></td>
            <td>
                <button 
                    className="btn btn-primary"
                    onClick={() => this.props.insertLine(this.state)}>Add to Sheet</button>
            </td>
        </tr>)
    }
}

const TimeSheetLine = (props) => {
    return(
        <tr>
           <td>{props.data.date}</td>
           <td>{props.data.timeIn}</td>
           <td>{props.data.timeOut}</td> 
           <td>{props.data.breaksTaken}</td>
           <td>00:00</td>
        </tr>
    )
}
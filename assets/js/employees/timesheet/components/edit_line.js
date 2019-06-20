import React, { Component } from 'react';
import DayField from './day_field';
import TimeField from '../../../src/components/time_field';

class EditLine extends Component{
    state = {
        date: parseInt(this.props.initData.date.split('-')[2]),
        timeIn: this.props.initData.timeIn.substring(0, 5),
        timeOut: this.props.initData.timeOut.substring(0, 5),
        breaksTaken: this.props.initData.breaksTaken.substring(0, 5),
        
    }
    timeHandler = (data, field) =>{
        if(data.valid){
            let newState = {...this.state};
            newState[field] = data.value;
            this.setState(newState);
        }   
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
                    handler={this.inputHandler}
                    initial={parseInt(this.props.initData.date.split('-')[2])}
                     /></td>
            <td><TimeField 
                    name="timeIn" 
                    handler={this.timeHandler}
                    initial={this.props.initData.timeIn.substring(0, 5)}/></td>
            <td><TimeField 
                    name="timeOut" 
                    handler={this.timeHandler}
                    initial={this.props.initData.timeOut.substring(0, 5)}/></td>
            <td><TimeField 
                    name="breaksTaken" 
                    handler={this.timeHandler}
                    initial={this.props.initData.breaksTaken.substring(0, 5)}
                    /></td>
            <td>Calculating...</td>
            <td>
                <button 
                    type="button"
                    className="btn btn-success"
                    onClick={() => this.props.editHandler(this.state, this.props.index)}>Confirm</button>
            </td>
        </tr>)
    }
}

export default EditLine;
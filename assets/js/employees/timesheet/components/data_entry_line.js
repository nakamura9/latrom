import React, {Component} from 'react';
import DayField from './day_field';
import TimeField from '../../../src/components/time_field';


class DataEntryLine extends Component{
    state = {
        date: 0,
        timeIn: 0,
        timeOut: 0,
        breaksTaken: 0
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
                    initial=""
                    /></td>
            <td><TimeField 
                    name="timeIn" 
                    handler={this.timeHandler}
                    initial=""
                    /></td>
            <td><TimeField 
                    name="timeOut" 
                    handler={this.timeHandler}
                    initial=""
                    /></td>
            <td><TimeField 
                    name="breaksTaken" 
                    handler={this.timeHandler}
                    initial=""
                    /></td>
            <td colSpan={2}>
                <button 
                    type="button"
                    className="btn btn-primary btn-block"
                    onClick={() => this.props.insertLine(this.state)}>Add to Sheet</button>
            </td>
        </tr>)
    }
}

export default DataEntryLine;
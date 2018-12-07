import React, {Component} from 'react';
import TimeField from '../../../src/components/time_field';
import AsyncSelect from '../../../src/components/async_select';


class ShiftEntry extends Component{
    state = {
        shift: "",
        startTime: "",
        endTime: "",
        monday: false,
        tuesday: false,
        wednesday: false,
        thursday: false,
        friday: false,
        saturday: false,
        sunday: false
    }
    shiftHandler = (data) =>{
        this.setState({shift: data});
    }
    
    timeHandler = (data, name) =>{
        if(data.valid){
            let newState = {...this.state};
            newState[name] = data.value;
            this.setState(newState)
        }
    }
    dayHandler = (evt) =>{
        let newState = {...this.state};
        
        newState[evt.target.name] = !this.state[evt.target.name];
        this.setState(newState);

    }
    render(){
        return(
            <tfoot>
                <tr className="bg-primary text-white">
                    <td>
                        <AsyncSelect 
                            dataURL="/manufacturing/api/shift"
                            resProcessor={(res) =>{
                                return (res.data.map((shift, i) =>(
                                    {
                                        value: shift.id + '-' + shift.name,
                                        name: shift.name
                                    }
                                )))
                            }}
                            handler={this.shiftHandler}/>
                    </td>
                    <td><TimeField   
                            name="startTime"
                            handler={this.timeHandler}/></td>
                    <td><TimeField   
                            name="endTime"
                            handler={this.timeHandler}/></td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.monday}
                            onChange={this.dayHandler}
                            name="monday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.tuesday}
                            onChange={this.dayHandler}
                            name="tuesday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.wednesday}
                            onChange={this.dayHandler}
                            name="wednesday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.thursday}
                            onChange={this.dayHandler}
                            name="thursday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.friday}
                            onChange={this.dayHandler}
                            name="friday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.saturday}
                            onChange={this.dayHandler}
                            name="saturday" />
                    </td>
                    <td>
                        <input 
                            type="checkbox"
                            className="form-control"
                            value={this.state.sunday}
                            onChange={this.dayHandler}
                            name="sunday" />
                    </td>
                    <td></td>
                </tr>
            <tr className="bg-primary text-white">
                <td colSpan={11}>
                    <button 
                        style={{
                            float: 'right'
                        }}
                        onClick={() => this.props.insertHandler(this.state)}
                        className="btn">
                            Insert
                    </button>
                </td>
            </tr>
            </tfoot>
        )
    }
}
export default ShiftEntry;
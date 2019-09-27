import React, { Component } from 'react';
import styles from './time.css'

/**
 * props
 * initial - string either "" or time in the form of HH:MM
 * handler - function that takes the state of the element and its name as args
 * name - string representing the inputs name
 */

class TimeField extends Component{
    state = {
        value: this.props.intial === "" 
                    ? "HH:MM"
                    : this.props.initial,
        valid: false,
        showPicker: false
    }

    componentDidMount = () => {
      this.setState({valid: !(this.props.initial === "")});
    }
    
    componentDidUpdate(prevProps, prevState){
        if(this.props.resetFlag && this.props.resetFlag != prevProps.resetFlag){
            this.setState({
                valid: false,
                value: "HH:MM"
            })
        }
    }

    handler = (evt) => {

        const value = evt.target.value;
        if(value.length == 2){
            this.setState({value: value + ":"});
            return;
        }
        const valid = /[012]\d:[0-5]\d/.test(value);
        this.setState({
            value: value,
            valid: valid
        }, () => this.props.handler(this.state, this.props.name));
    }

    togglePicker = () =>{
        this.setState((prevState) =>({
            showPicker: !prevState.showPicker
        }))
    }

    setTime = (pickerState) =>{
        this.setState({
            valid: true,
            value: pickerState.hour + ':' + pickerState.minute
        }, () => this.props.handler(this.state, this.props.name))
    }


    render(){
        return(
            <div style={{position: 'relative'}}>
            <input 
                type="text"
                value={this.state.value}
                onChange={this.handler}
                onClick={this.togglePicker}
                className="form-control"
                placeholder="HH:MM"
                style={{
                    border: `${this.state.valid ? '0' : '3' }px solid red`
                }} />
                {this.state.showPicker ? <Picker 
                                            setTime={this.setTime}
                                            hidePicker={this.togglePicker}/>: null}
            </div>
        )
    }
}

class Picker extends Component {
    state= {
        hour: '00',
        minute: '00'
    }
    
    hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',  
        '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 
        '23']
    
    minutes = this.hours.concat(['24', '25', '26', '27', '28', '29', '30', '31',
        '32', '33', '34', '35', '36', '37','38', '39', '40', '41', '42', '43', 
        '44', '45', '46', '47','48', '49', '50', '51', '52', '53', '54', '55',
        '56','57', '58','59'])
    
    selectHour = (value) =>{
        this.setState({hour: value})
    }
    selectMinute = (value) =>{
        this.setState({minute: value})
    }

    setTime = () =>{
        this.props.setTime(this.state)
        this.clearTime()
    }

    clearTime =() =>{
        this.setState({
            hour: '00',
            minute: '00'
        })
        this.props.hidePicker()
    }

    render(){
        const dataLists = {
            'display': 'inline-block',
            'maxHeight': '150px',
            'overflowY': 'auto'
        }
        
        
        return(
            <div style={{color: 'black', 
                        backgroundColor: 'white', 
                        zIndex: 1000, 
                        position: 'absolute', 
                        'left': '0px', 
                        'top': '40px', 
                        padding: '15px 7px',
                        width: 'fit-content'
                    }}>
                <div>
                    <h5 style={{textAlign:'center'}}>{this.state.hour}:{this.state.minute}</h5>
                </div>
                <div>
                    <div style={dataLists}>
                        <h6>Hour</h6>
                        <ul className={styles.time_list}>
                            {this.hours.map((i) =>(
                                <li style={{
                                    color: this.state.hour === i ? 
                                        'white' : '#007bff',
                                    backgroundColor: this.state.hour === i ? 
                                    '#007bff' : 'white'
                                }}
                                    className={styles.time_list_item}
                                    onClick={() => this.selectHour(i)}>{i}</li>
                            ))}
                        </ul>
                    </div>
                    <div style={dataLists}>
                        <h6>Min</h6>
                        <ul className={styles.time_list}>
                        {this.minutes.map((i) =>(
                            <li style={{
                                color: this.state.minute === i ? 
                                    'white' : '#007bff',
                                backgroundColor: this.state.minute === i ? 
                                '#007bff' : 'white'
                            }}
                                className={styles.time_list_item}
                                onClick={() => this.selectMinute(i)}>{i}</li>
                        ))}
                        </ul>

                    </div>
                </div>
                <div className="btn-group">
                <button type='button' onClick={this.setTime} className="btn btn-primary btn-sm"> <i className="fas fa-clock"></i> Set</button>
                <button type='button' onClick={this.clearTime} className="btn btn-secondary btn-sm"> <i className="fas fa-times"></i> Clear</button>
                </div>
            </div>
        )
    }

}

export default TimeField;
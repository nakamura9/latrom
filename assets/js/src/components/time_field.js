import React, { Component } from 'react';

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
        valid: false 
    }

    componentDidMount = () => {
      this.setState({valid: !(this.props.initial === "")});
    }
    

    handler = (evt) => {
        const value = evt.target.value;
        const valid = /[012]\d:[0-5]\d/.test(value);
        this.setState({
            value: value,
            valid: valid
        }, () => this.props.handler(this.state, this.props.name));
    }


    render(){
        return(
            <input 
                type="text"
                value={this.state.value}
                onChange={this.handler}
                className="form-control"
                placeholder="HH:MM"
                style={{
                    border: `${this.state.valid ? '0' : '3' }px solid red`
                }} />
        )
    }
}

export default TimeField;
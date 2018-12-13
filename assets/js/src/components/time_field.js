import React, { Component } from 'react';

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
                    border: `${this.state.valid ? '0' : '1' }px solid red`
                }} />
        )
    }
}

export default TimeField;
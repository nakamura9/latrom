import React, {Component} from 'react';

class SelectWidget extends Component{
    state = {
        selected: ''
    }

    handleChange =(evt) =>{
        this.setState({selected: evt.target.value});
        this.props.handler(evt.target.value);
    }
    render(){
        console.log(this.props.options)
        return(
            <select className='form-control' selected={this.state.selected}
                onChange={this.handleChange}>
                {this.props.options.map((option)=>(
                    <option value={option.value}>{option.label}</option>
                ))}
            </select>
        )
    }
}

export default SelectWidget
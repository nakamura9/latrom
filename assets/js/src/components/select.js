import React, {Component} from 'react';

class SelectWidget extends Component{
    state = {
        selected: ''
    }

    handleChange =(evt) =>{
        this.setState({selected: evt.target.value});
        this.props.handler(evt.target.value);
    }

    componentDidUpdate(prevProps, prevState){
        if(this.props.resetFlag && this.props.resetFlag != prevProps.resetFlag){
            this.setState({selected: ""})
        }
    }

    render(){
        return(
            <select 
                className='form-control' 
                selected={this.state.selected}
                onChange={this.handleChange}>
                <option value='' selected={this.state.selected==""}>--------</option>
                {this.props.options.map((option)=>(
                    <option value={option.value}>{option.label}</option>
                ))}
            </select>
        )
    }
}

export default SelectWidget
import React from 'react';

class HeaderStyleDropdown extends React.Component{
    onToggle = (evt) =>{
        let value = evt.target.value;
        this.props.onToggle(value);
    }
    
    render(){
        return (<select 
                    className="form-control" 
                    onChange={this.onToggle} 
                    value={this.props.active}
                    style={{display: 'inline-block', width: '40%'}}>
            <option value="">Heading Level</option>
            {this.props.headerOptions.map(heading =>{
                return(
                    <option value={heading.style}>{heading.label}</option>
                )
            })}
        </select>)
    }
}

export default HeaderStyleDropdown;
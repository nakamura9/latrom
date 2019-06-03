import React from 'react';

class BlockStyleButton extends React.Component{
    onToggle = (evt) =>{
        evt.preventDefault();
        this.props.onToggle(this.props.style);
    }

    render(){
        let className = "btn"
        if(this.props.active){
            className += " btn-primary"
        }

        return(
            <span className={className} onClick={this.onToggle}>{this.props.label}</span>
        )
    }
}

export default BlockStyleButton;
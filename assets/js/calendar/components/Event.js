import React from 'react';
const event = (props) =>{
    return(
        <div>
            <i className="{props.data.icon}"></i>
            <span>{props.label}</span>
        </div>
    );
}

export default event;
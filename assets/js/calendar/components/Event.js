import React from 'react';
const event = (props) =>{
    
    let description = null;
    if (props.description){
        description = (<div>
                        <p>{props.description}</p>
                    </div>);
        }
    let style = {
        margin: '2px',
        padding: '5px',
        color: 'white',
        backgroundColor: 'slateblue'
    };
    return(
        <div style={style}>
            <div>
                <i className={"fas fa-" + props.data.icon}></i>
                <span style={{margin: "0px 5px"}}>{props.data.label}</span>
            </div>
            {description}
        </div>
    );
}

export default event;
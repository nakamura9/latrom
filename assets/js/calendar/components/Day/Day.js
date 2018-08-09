import React from 'react';
import Event from '../Event';


const day = (props) => {
    let dayWrapper ={
        minWidth: "150px",
        minHeight: "100px",
        padding:"5px"
    };
    return(
        <div style={dayWrapper}>
            <div >
                <span style={{float:'right'}}>
                    <h4>{props.data.day}</h4>
                </span>
            </div>
            <div>
                {props.data.events.map((event, i) =>(
                    <Event key={i} label={event}/>
                ))}
            </div>
        </div>
    )
}

export default day;
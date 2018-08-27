import React from 'react';
import Event from '../Event';

const dayView = (props) =>{
    let dayWrapper = {
        width: '350px',
        height: '500px',
        margin: 'auto',
        padding: '10px',
        border: '1px solid black'
    } 
    let dayHeader = {
        textAlign:'center',
        backgroundColor: 'slateblue',
        borderBottom: '1px solid black',
        color: 'white',
        padding: '5px'
    }
    console.log(props.data);
    return(
        <div style={dayWrapper}>
            <div style={dayHeader}>
                <span >
                    <h1>{props.data.date}</h1>
                </span>
            </div>
            <div>
                {props.data.events.map((event, i) =>(
                    <Event key={i} data={event}/>
                ))}
            </div>
        </div>
    )
}

export default dayView;
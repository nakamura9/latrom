import React from 'react';
import Event from '../Event';


const day = (props) => {
    let dayWrapper = null;
    
    if (props.view === 'month'){
        dayWrapper={
            minWidth: "150px",
            minHeight: "100px",
            padding:"5px"
        }
    }else if (props.view === 'week'){
        dayWrapper={
            minWidth: "150px",
            minHeight: "300px",
            padding:"10px"
        }
    }else{
        dayWrapper={
            minWidth: "150px",
            minHeight: "100px",
            padding:"5px"
        }
    }
    return(
        <div style={dayWrapper}>
            <div style={{
                clear:'both',
                width:'100%',
                height:'30px'
            }}>
                <span style={{float:'right'}}>
                    <h4>{props.data.day}</h4>
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

export default day;
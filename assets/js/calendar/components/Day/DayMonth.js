import React from 'react';
import Event from '../Event';

const dayMonth = (props) => {
    //calculate the dimensions of the day
    let labelStyle = {
        clear:'both',
        width:'100%',
        height:'30px',
        };
    let dayWrapper={
            minWidth: `${props.width}px`,//here
            minHeight: `${props.height}px`,
            padding:"5px"
        };
    

    let eventList = null;
    const nEvents = props.data.events.length;    
    eventList = props.data.events;
    
    
    return(
        <div style={dayWrapper}>
            
            <div style={labelStyle}>
                <span style={{
                    float:'right'
                }}><h4>
                        <a href={`/calendar/day/${props.data.date}`}>
                            {props.data.day}</a> 
                    </h4>
                </span>
            </div>
            <div 
                style={{
                    position: "relative",
                    width: `${props.width}px`,//here
                    height:`${props.height}px`
                }}>
            {eventList.length < 2 ? 
                eventList.map((event, i) =>(
                    <Event 
                        width={props.width}
                        key={i} 
                        data={event}
                        view={props.view}/>
                ))
                :
                    <div style={{
                        padding: '5px',
                        backgroundColor: '#007bff',
                        width: '100%',
                    }}>
                    <a style={{
                        textDecoration: 'none',
                        color: 'white'
                    }} href={`/calendar/day/${props.data.date}`}>({eventList.length}) Events</a>
                    </div>
            }
            </div>
        </div>
    )
}

export default dayMonth;
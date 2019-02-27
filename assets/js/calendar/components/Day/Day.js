import React from 'react';
import Event from '../Event';

const day = (props) => {
    let dayWrapper = null;
    let dayLabel = 
        <span style={{
            float:'right'
        }}><h4>
                <a href={`/calendar/day/${props.data.date}`}>
                    {props.data.day}</a> 
            </h4>
        </span>;
    if (props.view === 'month'){
        dayWrapper={
            minWidth: "150px",
            minHeight: "150px",
            padding:"5px"
        }
    }else if (props.view === 'week'){
        dayWrapper={
            minWidth: "200px",
            minHeight: "400px",
            padding:"10px"
        }
    }else{ //day
        dayLabel = 
        <h1 style={{
            color: 'white',
            backgroundColor: '#07f',
            padding: '30px',
            clear: "both",
            float: "left",
            width: "720px"        
        }}>{props.data.date}</h1>
        dayWrapper={
            minWidth: "400px",
            minHeight: "150px",
            padding:"5px",
            border: '1px solid #0cf'
        }
    }

    

    let eventList = null;
    const nEvents = props.data.events.length;    
    eventList = props.data.events;
    
    //on click handler for date numbers
    const intervals = ['00:00', '01:00', '02:00', '04:00', '05:00', '06:00', 
        '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', 
        '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
        '21:00', '22:00', '23:00'  
    ]
    const hourByHour = 
        <table style={{
            width: props.view === "day" ? "720px" : "200px",
            position: "absolute",
            top: "90px"
        }}>
            {intervals.map((time, i) =>(
                <tr 
                    height={20}
                    key={i} 
                    style={{
                    borderTop: "1px solid black",
                    minHeight: "20px",
                    
                }}>
                    <td style={{width: "20%"}}>{time}</td>
                    <td style={{
                        width: "80%",
                    }}>&nbsp;</td>
                </tr>
            ))}
        </table>
    return(
        <div style={dayWrapper}>
            
            <div style={{
                clear:'both',
                width:'100%',
                height:'30px'
                }}>
                {dayLabel}
            </div>
            <div 
                id="day content"
                style={{
                    position: "relative",
                    width: props.view === "day" ? "720px" : "200px",
                    height: props.view === "month" ? "100px" : "640px",
                }}>
            {props.view === "month" ? null : hourByHour}
            {eventList.map((event, i) =>(
                <Event 
                    key={i} 
                    data={event}
                    view={props.view}/>
            ))}
            </div>
        </div>
    )
}
export default day;
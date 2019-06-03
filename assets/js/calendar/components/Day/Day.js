import React from 'react';
import Event from '../Event';

const day = (props) => {
    //calculate the dimensions of the day
    let dayWrapper = null;
    let dayLabel = 
        <span style={{
            float:'right'
        }}><h4>
                <a href={`/calendar/day/${props.data.date}`}>
                    {props.data.day}</a> 
            </h4>
        </span>;
    if (props.view === 'week'){
        dayWrapper={
            minWidth: `${props.width}px`,
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
            minWidth: "740px",
            minHeight: "500px",
            padding:"10px",
            border: '2px solid  #007bff',
            borderRadius: '5px',
            overflowY: 'auto',
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
    // only week and day views have an hourly breakdown therefore only two 
    // options
    const hourByHour = 
        <table style={{
            width: props.view === "day" ? "720px" : `${props.width}px`,
            position: "absolute",
            top: props.view === "day" ? "90px" : "0px"
        }}>
            <tbody>
                {intervals.map((time, i) =>(
                    <tr 
                        height={20}
                        key={i} 
                        style={{
                        borderTop: "1px solid #aaaaaa",
                        minHeight: "20px",
                        
                    }}>
                        <td style={{width: "20%"}}>{time}</td>
                        <td style={{
                            width: "80%",
                        }}>&nbsp;</td>
                    </tr>
                ))}
            </tbody>
        </table>
    return(
        <div style={dayWrapper}>
            
            <div style={{
                clear:'both',
                width:'100%',
                height:'30px',
                }}>
                {dayLabel}
            </div>
            <div 
                style={{
                    position: "relative",
                    width: props.view === "day" ? "720px" : `${props.width}px`,//here
                    height:  "640px",
                }}>
            {hourByHour}
            { eventList.map((event, i) =>(
                <Event 
                    width={props.width}
                    key={i} 
                    data={event}
                    view={props.view}/>
            ))}
            </div>
        </div>
    )
}


export default day;
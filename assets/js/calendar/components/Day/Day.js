import React from 'react';
import Event from '../Event';

const day = (props) => {
    let dayWrapper = null;
    
    if (props.view === 'month'){
        dayWrapper={
            minWidth: "200px",
            minHeight: "150px",
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
            minHeight: "150px",
            padding:"5px"
        }
    }
    let eventList = null;
    const nEvents = props.data.events.length;
    if ( nEvents > 2){
        eventList = props.data.events.splice(0, 2);
        eventList.push({
            icon: 'share',
            label:  '+ ' + (nEvents - 2) + ' more event(s)'
        });
    }else{
        eventList = props.data.events;
    }
    //on click handler for date numbers

    return(
        <div style={dayWrapper}>
            <div style={{
                clear:'both',
                width:'100%',
                height:'30px'
            }}>
                <span style={{float:'right'}}>
                    <h4>
                        {props.data.day}
                    </h4>
                </span>
            </div>
            <div>
                {eventList.map((event, i) =>(
                    <Event key={i} data={event}/>
                ))}
            </div>
        </div>
    )
}

export default day;
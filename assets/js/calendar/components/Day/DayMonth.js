import React from 'react';
import Event from '../Event';
import styles from './Day.css';

const dayMonth = (props) => {
    //calculate the dimensions of the day
    const windowWidth = document.documentElement.clientWidth;
    const sidebarWidth = document.getElementById('sidebar').offsetWidth;
    const calendarWidth = windowWidth - sidebarWidth;
    const cellWidth = (calendarWidth - 15 /**8-5 + !!2 */) / 7;

    const daysLabelHeight = 32;
    const navBarHeight = document.getElementById('navbar').offsetHeight;
    const windowHeight = document.documentElement.clientHeight;
    const contentHeight = windowHeight - daysLabelHeight - navBarHeight;
    const cellHeight = (contentHeight -5)/ 5;

    let labelStyle = {
        clear:'both',
        width:'100%',
        height:'30px',
        };
    let dayWrapper={
            width: `${cellWidth}px`,//here
            height: `${cellHeight}px`,
        };
    

    let eventList = null;
    const nEvents = props.data.events.length;    
    eventList = props.data.events;
    
    
    return(
        <div style={dayWrapper}>
            
            <div style={labelStyle}>
                <span style={{
                    float:'right'
                }}><h5>
                        <a href={`/calendar/day/${props.data.date}`}>
                            {props.data.day}</a> 
                    </h5>
                </span>
            </div>
            <div 
                style={{
                    position: "relative",
                    width: `100%`,//here
                    height:`2rem`
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
                    <div className={styles.eventBox}>
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
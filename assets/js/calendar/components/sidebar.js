import React from 'react';
import MiniCalendar from '../components/mini_calendar';
import {BrowserRouter as Router, Route, Link} from 'react-router-dom';

const sidebar = (props) =>{
    const sidebarStyle = {
        backgroundColor: "#07f",
        display: "inline-block",
        float: 'left',
        'minHeight':'500px',
        width: '250px',
        padding: '30px'
        
    };
    return(
        <div style={sidebarStyle}>
            <div className="btn-group">            
                <Link className="btn btn-primary" 
                    to={`/calendar/month/${props.calendarState.year}/${props.calendarState.month}`}><i className="fa fas-calendar"></i> Month</Link>
                <Link className="btn btn-primary" 
                    to={`/calendar/week/${props.calendarState.year}/${props.calendarState.month}/${props.calendarState.day}`}>Week</Link>
                <Link className="btn btn-primary" 
                    to={`/calendar/day/${props.calendarState.year}/${props.calendarState.month}/${props.calendarState.day}`}>Day</Link>
            </div>
            <div className="btn-group">
                <button
                    className="btn btn-primary"
                    onClick={props.prevHandler}>
                        <i className="fas fa-arrow-left"></i>
                </button>    
                <button
                    className="btn btn-primary"
                    onClick={props.nextHandler}>
                        <i className="fas fa-arrow-right"></i>
                </button>
            </div>
            <div>
                <MiniCalendar 
                    year={props.calendarState.year}
                    month={props.calendarState.month} />
            </div>
            <a href="/planner/event-create/"
               className="btn btn-primary">Create New Event</a>    
        </div>
    );
}

export default sidebar;